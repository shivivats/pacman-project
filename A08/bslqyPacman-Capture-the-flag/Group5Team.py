# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import numpy as np
import util
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent1', second = 'DummyAgent2'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class BaseAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.target_list = []

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """


    actions = gameState.getLegalActions(self.index)

    # deciding if it should attack or defend
    self.setMode(gameState)

    # retrieving action values in the 2c ases
    if self.attack:
      values = [self.evaluateAttack(gameState, a) for a in actions]
    else:
      values = [self.evaluateDefense(gameState,a)for a in actions]

    # choosing the action with the highest value
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    # if there is more than one action with the highest val choose randomly
    return random.choice(bestActions)


  def setMode(self, gameState):
    # choosing if go in attack or defend mode

    # list of opponent remaining food
    remaining_food = self.getFood(gameState).asList()
    #list of opponent remaining capsules
    capsules = self.getCapsules(gameState)

    # list of targets for our bot
    self.target_list = [food for food in self.target_list if food in remaining_food or food in capsules]

    # distance of opponent ghost agents
    ghosts_dists = self.getActiveGhostDistances(gameState)
    closest_ghost = min(ghosts_dists) if ghosts_dists else 20

    # checking if the agent is scared
    amScared = gameState.getAgentState(self.index).scaredTimer > 0

    # checking if we are carrying any food
    carrying = gameState.getAgentState(self.index).numCarrying

    # if we are currently attacking
    if self.attack:
      # and retrieved all target food, or we are chased by a ghost go back defending
      if len(remaining_food) <= 2 or not self.target_list or (closest_ghost <= 4 and carrying):
        self.attack = False

      amPacman = gameState.getAgentState(self.index).isPacman
      # if the agent is a ghost and is not scared and we are winning defend
      if not amPacman  and not amScared and self.getScore(gameState) > 0:
        self.attack = False
    else:
      # if wer are defending and we are loosing or we are scared attack
      if not carrying and (self.getScore(gameState) <= 0 or amScared):
        self.attack = True
        #self.target_list = remaining_food + capsules

  def getActiveGhostDistances(self, gameState):
    # retrieve ghost distances
    myPos = gameState.getAgentState(self.index).getPosition()
    opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    active_ghosts = [a for a in opponents if not a.isPacman and a.scaredTimer == 0 and a.getPosition() != None]
    active_ghosts_positions = [a.getPosition() for a in active_ghosts]
    ghosts_dists = [self.getMazeDistance(myPos, gp) for gp in active_ghosts_positions]
    return ghosts_dists

  def getAttackFeatures(self, gameState, action):
    # retrieving attack features
    features = util.Counter()
    # previous position before action
    prev_position = gameState.getAgentState(self.index).getPosition()
    # successor state for current action
    successor = self.getSuccessor(gameState, action)
    # position after action
    myPos = successor.getAgentState(self.index).getPosition()
    walls = successor.getWalls()
    amPacman = successor.getAgentState(self.index).isPacman

    # stopping is heavily penalized
    features["stop"] = 1 if action == Directions.STOP else 0

    # getting distance from closest active ghost
    opponents = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    active_ghosts = [a for a in opponents if not a.isPacman and a.scaredTimer == 0 and a.getPosition() != None]
    active_ghosts_positions = [a.getPosition() for a in active_ghosts]
    ghosts_dists = [self.getMazeDistance(myPos, gp) for gp in active_ghosts_positions]
    closest_ghost = min(ghosts_dists) if ghosts_dists and amPacman else 20
    features["closest_ghost_dist"] = closest_ghost

    # checking if we have an opponent ghost very close to us
    features["is_ghost_nearby"] = 1 if closest_ghost <= 4 else  0

    # penalizing states with lower amount of moves
    n_avaiable_actions = len(successor.getLegalActions(self.index))
    features["#_actions_danger"] = features["is_ghost_nearby"] * n_avaiable_actions

    # checking if the next step leads us to a deadend
    is_there_way_out = 0 if self.deadends[int(myPos[0])][int(myPos[1])] else 1

    # distance from a cell which is not a deadend
    dist_to_open_space = self.distanceToOpenSpace(myPos, active_ghosts_positions, walls)

    # checking dist to closest ghost before taking the action
    prev_ghosts_dists = [self.getMazeDistance(prev_position, gp) for gp in active_ghosts_positions]
    prev_closest_ghost = min(prev_ghosts_dists) if prev_ghosts_dists else 20
    was_ghost_nearby = 1 if prev_closest_ghost <= 5 and gameState.getAgentState(self.index).isPacman else 0

    # if we have a ghost nearby we want to avoid deadends and in case we are in a deadend we want to exit it
    features["danger_level"] = dist_to_open_space * (2 - is_there_way_out) * was_ghost_nearby

    # defining our targets
    if self.target_list:
      target_list = self.target_list
    else:
      remaining_food = self.getFood(gameState).asList()
      capsules = self.getCapsules(gameState)
      target_list = remaining_food + capsules

    # taking distance from closes target
    min_target_distance = min([self.getMazeDistance(myPos, t) for t in target_list])
    features["closest_target_dist"] = min_target_distance
    # if features["is_ghost_nearby"]:
    #   print(features)
    return features

  def getAttackWeights(self, gameState, action):
    return {"closest_target_dist" : -2, "closest_ghost_dist" : 3, "stop" : -100, "is_ghost_nearby" : -5, "#_actions_danger" : 1, "danger_level" : -10}

  def evaluateAttack(self, gameState, action):
    features = self.getAttackFeatures(gameState, action)
    weights = self.getAttackWeights(gameState, action)

    return features * weights

  def getDefenseFeatures(self, gameState, action):
    # extracting features for when we are defending
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    amPacman = myState.isPacman
    myFood = self.getFoodYouAreDefending(gameState).asList()

    # Computes whether we're on defense (1) or offense (0)
    # features['onDefense'] = 1
    # if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    # if we are ghosts
    if not amPacman:
      # if we see and invader go towards him
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['targetDistance'] = min(dists)
      else:
        # if we don't but a food disappeared go toward that food position
        self.recent_missing_food = self.recent_missing_food+[f for f in self.myPrevFood if f not in myFood]
        if self.recent_missing_food:
          #dists = [self.getMazeDistance(myPos, f) for f in self.recent_missing_food]
          features['targetDistance'] = self.getMazeDistance(myPos, self.recent_missing_food[-1])
    else:
      # if we are not ghosts go back to our side
      dists = [self.getMazeDistance(myPos,self.start)]
      features['targetDistance'] = min(dists)


    # stopping is heavily penalized
    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    self.myPrevFood = myFood
    return features

  def getDefenseWeights(self, gameState, action):
    return {'numInvaders': -1000, 'targetDistance': -10, 'stop': -100, 'reverse': -2}

  def evaluateDefense(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getDefenseFeatures(gameState, action)
    weights = self.getDefenseWeights(gameState, action)
    return features * weights

  def getFoodClusters(self, gameState):
    # identifying 2 clusters of food, one for each agent
    food_grid = self.getFood(gameState)
    food_positions = food_grid.asList()

    # removing furtherest away foods (from starting position)
    food_distances = [self.getMazeDistance(self.start, f) for f in food_positions]

    # removing the 2 most distant foods
    food_positions.remove(food_positions[food_distances.index(max(food_distances))])
    food_distances.remove(food_distances[food_distances.index(max(food_distances))])
    food_positions.remove(food_positions[food_distances.index(max(food_distances))])
    food_distances.remove(food_distances[food_distances.index(max(food_distances))])

    capsules_positions = self.getCapsules(gameState)
    complete_list = food_positions + capsules_positions

    X = np.array(complete_list)
    from sklearn.cluster import KMeans
    clusters = KMeans(n_clusters=2, random_state=0).fit(X)

    f_group1 = []
    f_group2 = []
    for i, f in enumerate(complete_list):
      if clusters.labels_[i] == 1:
        f_group1.append(f)
      else:
        f_group2.append(f)

    return f_group1, f_group2


  def getDeadends(self, gameState):
    # identifying the deadends
    walls = gameState.getWalls()

    deadends = [[0 for i in range(walls.height)] for j in range(walls.width)]
    added_deadends = True

    while added_deadends:
      added_deadends = False
      for i in range(1,walls.height-1):
        for j in range(1,walls.width-1):
          if not deadends[j][i] and not walls[j][i]:
            successors =[(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
            free_spots = 0
            for s in successors:
              if not walls[s[1]][s[0]] and not deadends[s[1]][s[0]]:
                free_spots+=1
            if free_spots <= 1:
              deadends[j][i] = 1
              added_deadends = True

    return deadends

  def distanceToOpenSpace(self, position, ghosts, walls):
    # calculating the distance from a non deadend
    from util import Queue
    if not self.deadends[int(position[0])][int(position[1])]: return 1

    my_queue = Queue()
    my_queue.push(position)
    path_lengths = {}
    path_lengths[str(position)] = 2
    visited = [position]
    while not my_queue.isEmpty():
      pos = my_queue.pop()

      successors = [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]
      for s in successors:
        if not walls[int(s[0])][int(s[1])] and not s in visited and not s in ghosts:
          visited.append(s)
          path_lengths[str(s)] = path_lengths[str(pos)] + 1
          if not self.deadends[int(s[0])][int(s[1])]:
            return path_lengths[str(s)]
          else:
            my_queue.push(s)

    return 999

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

class DummyAgent1(BaseAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    fgroup_1, fgroup_2 = self.getFoodClusters(gameState)
    self.target_list = fgroup_1
    self.attack = True
    self.deadends = self.getDeadends(gameState)
    self.myPrevFood = self.getFoodYouAreDefending(gameState).asList()
    self.recent_missing_food=[]

class DummyAgent2(BaseAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    fgroup_1, fgroup_2 = self.getFoodClusters(gameState)
    self.target_list = fgroup_2
    self.attack = True
    self.deadends = self.getDeadends(gameState)
    self.myPrevFood = self.getFoodYouAreDefending(gameState).asList()
    self.recent_missing_food = []











