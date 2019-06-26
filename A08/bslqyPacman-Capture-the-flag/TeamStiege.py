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
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'CollectorAgent', second = 'CollectorAgent'):
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


  start = """
  
  
    sSSSSs    sSSs_sSSs                                 
 d%%%%SP   d%%SP~YS%%b                                
d%S'      d%S'     `S%b                               
S%S       S%S       S%S                               
S&S       S&S       S&S                               
S&S       S&S       S&S                               
S&S       S&S       S&S                               
S&S sSSs  S&S       S&S                               
S*b `S%%  S*b       d*S                               
S*S   S%  S*S.     .S*S                               
 SS_sSSS   SSSbs_sdSSS                                
  Y~YSSY    YSSP~YSSY                                 
                                                      
                                                      
                                                      
sdSS_SSSSSSbs    sSSs   .S_SSSs     .S_SsS_S.         
YSSS~S%SSSSSP   d%%SP  .SS~SSSSS   .SS~S*S~SS.        
     S%S       d%S'    S%S   SSSS  S%S `Y' S%S        
     S%S       S%S     S%S    S%S  S%S     S%S        
     S&S       S&S     S%S SSSS%S  S%S     S%S        
     S&S       S&S_Ss  S&S  SSS%S  S&S     S&S        
     S&S       S&S~SP  S&S    S&S  S&S     S&S        
     S&S       S&S     S&S    S&S  S&S     S&S        
     S*S       S*b     S*S    S&S  S*S     S*S        
     S*S       S*S.    S*S    S*S  S*S     S*S        
     S*S        SSSbs  S*S    S*S  S*S     S*S        
     S*S         YSSP  SSS    S*S  SSS     S*S        
     SP                       SP           SP         
     Y                        Y            Y          
                                                      
  sSSs  sdSS_SSSSSSbs   .S    sSSs    sSSSSs    sSSs  
 d%%SP  YSSS~S%SSSSSP  .SS   d%%SP   d%%%%SP   d%%SP  
d%S'         S%S       S%S  d%S'    d%S'      d%S'    
S%|          S%S       S%S  S%S     S%S       S%S     
S&S          S&S       S&S  S&S     S&S       S&S     
Y&Ss         S&S       S&S  S&S_Ss  S&S       S&S_Ss  
`S&&S        S&S       S&S  S&S~SP  S&S       S&S~SP  
  `S*S       S&S       S&S  S&S     S&S sSSs  S&S     
   l*S       S*S       S*S  S*b     S*b `S%%  S*b     
  .S*P       S*S       S*S  S*S.    S*S   S%  S*S.    
sSS*S        S*S       S*S   SSSbs   SS_sSSS   SSSbs  
YSS'         S*S       S*S    YSSP    Y~YSSY    YSSP  
             SP        SP                             
             Y         Y                              
                                                   
  
  
  """



  print(start)

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class BaseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''

    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    chosen = random.choice(bestActions)

    return chosen

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)



    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}



GHOST_DISTANCE = 2
class CollectorAgent(BaseAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  CHASING = -1

  def cycleFound(self, successor, gameState):
    """Search the shallowest nodes in the search tree first."""

    queue = []
    queue.append([successor, gameState])
    visited = []

    while len(queue) > 0:
      current_element = queue.pop()
      current_state = current_element[0]
      previous_state = current_element[1]

      previous_position = previous_state.getAgentState(self.index).getPosition() if previous_state != None else None

      if current_state in visited:
        return True
      else:

        visited.append(current_state)

        actions = current_state.getLegalActions(self.index)
        successors = [self.getSuccessor(current_state, action) for action in actions if action != 'Stop']

        for successor in successors:
          successor_position = successor.getAgentState(self.index).getPosition()
          if previous_state == None or previous_position != successor_position:
            queue.append([successor, current_state])

    return False


  def getFoodForAgent(self, successor):
    """
    Divide set of food into two halfes and assign each one two an agent

    Only do this when no agent is chasing

    :param successor:
    :return:
    """
    if CollectorAgent.CHASING > -1:
      return []

    sortedFood = sorted(self.getFood(successor).asList(), key=lambda food: food[1])

    member = [member for member in self.getTeam(successor) if member != self.index][0]

    myPos = successor.getAgentState(self.index).getPosition()
    memberpos = successor.getAgentState(member).getPosition()

    if self.index > member:
      myFood = sortedFood[len(sortedFood)/2 : ]
    else:
      myFood = sortedFood[:len(sortedFood) / 2]

    return myFood


  def getFeaturesCollect(self):

    pass

  def chaseGhost(self, successor):
    member = [member for member in self.getTeam(successor) if member != self.index][0]

  def getDistanceToTeamMember(self, successor):
    """

    :param successor:
    :return:
    """
    member = [member for member in self.getTeam(successor) if member != self.index][0]

    myPos = successor.getAgentState(self.index).getPosition()
    memberpos = successor.getAgentState(member).getPosition()

    return self.getMazeDistance(myPos, memberpos)

  def getFeaturesBait(self, features, successor, gameState):

    enemy, minDistance = self._getDistanceToGhost(successor)

    bait = 0
    if minDistance < GHOST_DISTANCE:
      bait = -999 #never go towards ghost when near
    elif minDistance == GHOST_DISTANCE:
      cycleFound = self.cycleFound(successor, gameState)
      bait = 999 + (2000 if cycleFound else 0)
      CollectorAgent.CHASING = self.index
    features['bait'] = bait



  def _getDistanceToGhost(self, successor):
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    enemyGhosts = [enemy for enemy in enemies if not enemy.isPacman and enemy.getPosition() != None]

    if len(enemyGhosts) != 0:
      myPos = successor.getAgentState(self.index).getPosition()
      (e, minDistance) = min([(enemy, self.getMazeDistance(myPos, enemy.getPosition())) for enemy in enemyGhosts], key=lambda x: x[1])
      return (e, minDistance)

    return (None, -1)


  def _getDistanceToPacman(self, successor):
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    enemyPacman = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]

    if len(enemyPacman) != 0:
      myPos = successor.getAgentState(self.index).getPosition()
      (e, minDistance) = min([(enemy, self.getMazeDistance(myPos, enemy.getPosition())) for enemy in enemyPacman], key=lambda x: x[1])
      return (e, minDistance)

    return (None, -1)

  def enemyKilled(self, successor):
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    killedEnemies = [enemy for enemy in enemies if enemy.configuration == enemy.start]
    return len(killedEnemies)

  def getFeatures(self, gameState, action):
    """
    main feature getting method

    :param gameState:
    :param action:
    :return:
    """
    features = util.Counter()

    successor = self.getSuccessor(gameState, action)

    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)

    # Compute distance to the nearest food
    myPos = successor.getAgentState(self.index).getPosition()
    myFood = self.getFoodForAgent(successor)

    returnToStart = len(foodList) <= 2

    if not returnToStart:
      if gameState.getAgentState(self.index).getPosition() == self.start:
        CollectorAgent.CHASING = -1

      if len(foodList) > 0:  # This should always be True,  but better safe than sorry
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance

      if len(myFood) > 0:  # This should always be True,  but better safe than sorry
        minDistance = min([self.getMazeDistance(myPos, food) for food in myFood])
        features['distanceToMyFood'] = minDistance


    enemy, minDistance = self._getDistanceToGhost(successor)
    flee = 0
    bait = 0
    chase = 0

    if not successor.getAgentState(self.index).isPacman: #is ghost
      enemyPacman, distanceToEnemyPacman = self._getDistanceToPacman(successor)

      if successor.getAgentState(self.index).scaredTimer:
        flee = distanceToEnemyPacman
      elif distanceToEnemyPacman >= 0 and distanceToEnemyPacman < 2:
        features["bait"] = 1000 - distanceToEnemyPacman * 50
      elif self.enemyKilled(successor):
        chase = 1000

    else:

      # DO EAT ENEMY
      if enemy != None and enemy.configuration == enemy.start:
        chase = 1000
      if enemy != None and enemy.scaredTimer > 0 and not returnToStart:
        chase = 1000 - minDistance * 10
      elif minDistance > 0 and minDistance <= GHOST_DISTANCE and (CollectorAgent.CHASING == self.index or CollectorAgent.CHASING < 0) and not returnToStart:
        self.getFeaturesBait(features, successor,gameState)
      elif minDistance > 0:
        if minDistance < 5:
          cycleFound = self.cycleFound(successor, gameState)
          bait = minDistance + (50 if cycleFound else 0)
        else:
          bait = 100

    features['returnToStart'] = 0 if not returnToStart else -self.getMazeDistance(myPos, self.start)

    # stopping is considered bad behaviour

    features["stop"] = 100 if action == "Stop" else 0
    features["chase"] = chase

    features["nearMember"] = self.getDistanceToTeamMember(successor) // 2

    features['flee'] = flee
    features["bait"] = features["bait"] if features["bait"] != 0 else bait
    numCarrying = successor.getAgentState(self.index).numCarrying

    #going away from start is bad
    #features['bringBack'] = -numCarrying * self.getMazeDistance(myPos, self.start)# distance to start

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToMyFood': -1, 'bait': 100, "nearMember": 1, "stop": -100, "flee": 200, "chase": 100, "returnToStart": 190 }
