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
import random

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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

class OffensiveReflexAgent(CaptureAgent):
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
    #self.start = gameState.getAgentPosition(self.index)

    if self.red:
        centralX = (gameState.data.layout.width - 2) / 2
    else:
        centralX = ((gameState.data.layout.width - 2) / 2) + 1
    self.boundary = []
    for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(centralX, i):
            self.boundary.append((centralX, i))
    self.nearestFood = self.getFurthestTarget(gameState, gameState.getAgentState(self.index).getPosition(), self.getFood(gameState).asList())
    self.team = self.getTeam(gameState)
    self.opponent = self.getOpponents(gameState)
    self.randFoodStatus = 0
    self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
    if self.index == self.team[0]:
        self.partnerIndex = self.team[1]
    else:
        self.partnerIndex = self.team[0]

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    x, y = gameState.getAgentState(self.index).getPosition()
    myPos = (int(x), int(y))
    actions = gameState.getLegalActions(self.index)
    if len(actions) > 0:
        actions.remove(Directions.STOP)
    foods = self.getFood(gameState).asList()
    if self.red:
        capsules = gameState.getBlueCapsules()
    else:
        capsules = gameState.getRedCapsules()
    foods += capsules

    partnerPos = gameState.getAgentState(self.partnerIndex).getPosition()


    if self.nearestFood not in foods:
        mindis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)

    if len(foods) > 2:

        scaredTimes = [gameState.getAgentState(i).scaredTimer for i in self.opponent]

        opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

        if len(opponentGhosts) == 2:
            #print("2")
            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]
            if opponent1 is not None and opponent2 is not None and (scaredTimes[0] <= 5 or scaredTimes[1] <= 5):

                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()

                if len(capsules) > 0:

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    if distToCap < self.getMazeDistance(opponent1Pos, nearestCapsule) & distToCap < self.getMazeDistance(opponent2Pos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action
                if self.getMazeDistance(myPos, opponent1Pos) <= 5 or self.getMazeDistance(myPos, opponent1Pos) <= 5:

                    if gameState.getAgentState(self.index).isPacman:
                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c", "door", nearestDoor, minDis)
                        return action


                    else:
                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b", "randfood", self.randFood, minDis)
                            return action

                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z", "suiside", nearestFood, minDis)
                                return action
                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action
        elif len(opponentGhosts) == 1:
            #print("1")
            opponent = opponentConfig[0]
            if opponent is not None and gameState.getAgentState(opponentGhosts[0]).scaredTimer <= 5:

                opponentPos = opponent.getPosition()

                if len(capsules) > 0:

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    if distToCap < self.getMazeDistance(opponentPos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                if self.getMazeDistance(myPos, opponentPos) <= 5:

                    if gameState.getAgentState(self.index).isPacman:

                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c-2", "door", nearestDoor, minDis)
                        return action
                    else:
                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z-2", "suiside", nearestFood, minDis)
                                return action

                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-1", "randfood", self.randFood, minDis)
                            return action

                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action

        if self.randFoodStatus > 0:
            minDis, action = self.getBestAction(gameState, self.randFood, actions)
            self.randFoodStatus -= 1
            #print(self.index, "countdown", self.randFood, minDis, self.randFoodStatus)
            return action

        partnerMinDisttoFood, partnerNearestFood = self.getNearestTarget(gameState, partnerPos, foods)
        myMinDisttoFood, myNearestFood = self.getNearestTarget(gameState, myPos, foods)
        minDisttoHome, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)

        if gameState.getAgentState(self.index).numCarrying > minDisttoHome:
            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
            #print(self.index, "g", "door", nearestDoor, minDis)
            return action

        if myNearestFood == partnerNearestFood:

            if myMinDisttoFood < partnerMinDisttoFood:
                self.nearestFood = myNearestFood
            elif myMinDisttoFood == partnerMinDisttoFood:
                if self.index == self.team[0]:
                    if self.getMazeDistance(myPos, self.nearestFood) <= myMinDisttoFood:
                        self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
                else:
                    self.nearestFood = myNearestFood
            else:
                if self.nearestFood == myNearestFood:
                    self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
        else:
            self.nearestFood = myNearestFood

        minDis, action = self.getBestAction(gameState, self.nearestFood, actions)
        #print(self.index, "h", "food", self.nearestFood, minDis)
        return action

    else:
        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
        #print(self.index, "i", "door", nearestDoor, minDis)
        return action


  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)


  def getFurthestTarget(self, gameState, pos, targets):
    maxDisttoTarget, furthestTarget = max([(self.getMazeDistance(pos, target), target) for target in targets])
    return furthestTarget

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
        return pos

  def getBestAction(self, gameState, targetPos, actions):
    minDis, bestAction = min([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
    #print("best action", minDis, action)
    #print([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
    return (minDis, bestAction)

  def isAtDoor(self, gameState):
    myPos = gameState.getAgentState(self.index).getPosition()
    if myPos in self.boundary:
        return True
    else:
        return False


class DefensiveReflexAgent(CaptureAgent):
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
    #self.start = gameState.getAgentPosition(self.index)

    if self.red:
        centralX = (gameState.data.layout.width - 2) / 2
    else:
        centralX = ((gameState.data.layout.width - 2) / 2) + 1
    self.boundary = []
    for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(centralX, i):
            self.boundary.append((centralX, i))
    self.nearestFood = self.getFurthestTarget(gameState, gameState.getAgentState(self.index).getPosition(), self.getFood(gameState).asList())
    self.team = self.getTeam(gameState)
    self.opponent = self.getOpponents(gameState)

    #print "opponents" + str(self.opponent)
    self.randFoodStatus = 0
    self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
    if self.index == self.team[0]:
        self.partnerIndex = self.team[1]
    else:
        self.partnerIndex = self.team[0]
    self.nearestBoundary = (1,1)
    self.powerPillUsed=False;
    self.currentBoundaryIndex=0;
    self.behindBoundary = []
    if self.red:
        centralBehindX = (gameState.data.layout.width - 2) / 2 -2
    else:
        centralBehindX = ((gameState.data.layout.width - 2) / 2) + 1 + 2
    for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(centralBehindX, i):
            self.behindBoundary.append((centralBehindX, i))

    self.pacmanHuntDistance = 6
    self.lastKnownEnemyPacmanPosition = random.choice(self.behindBoundary)
    self.wantToGoAfterPacmanInHuntMode = False
    self.lastNumberOfPacman = 0

  def chooseAction(self, gameState):
    """
    Border patrol.
    """
    x, y = gameState.getAgentState(self.index).getPosition()
    myPos = (int(x), int(y))
    actions = gameState.getLegalActions(self.index)
    if len(actions) > 0:
        actions.remove(Directions.STOP)
    foods = self.getFood(gameState).asList()
    if self.red:
        capsules = gameState.getBlueCapsules()
    else:
        capsules = gameState.getRedCapsules()
    foods += capsules

    defendFood = self.getFoodYouAreDefending(gameState).asList()

    partnerPos = gameState.getAgentState(self.partnerIndex).getPosition()

    minBoundaryDistance, self.nearestBoundary = self.getNearestTarget(gameState, myPos, self.boundary)

    if self.nearestFood not in foods:
        mindis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)

    # ghost loses configuration hence he stops going after them so implement furthestTarget
    # can also decrease the distance threshold to pacman for kill tomorrow
    #

    # if less than 2 foods, go into super hunt mode
    if len(defendFood) <= 5:
        self.pacmanHuntDistance = 50

    # if more than 2 foods

    if not self.powerPillUsed:

        #  do something

        opponentPacmans = [i for i in self.opponent if gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentPacmans]

        #print "pacman config" +str(opponentConfig)

        if len(opponentPacmans) == 2:

            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]
            if opponent1 is not None and opponent2 is not None:
                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()
                opponent1index = opponentPacmans[0]
                opponent2index = opponentPacmans[1]

                if gameState.getAgentState(opponent1index).numCarrying >= gameState.getAgentState(opponent2index).numCarrying:
                    if self.getMazeDistance(myPos, opponent1Pos) < self.pacmanHuntDistance:
                        self.lastKnownEnemyPacmanPosition = opponent1Pos
                        self.wantToGoAfterPacmanInHuntMode = True
                        minDis, action = self.getBestAction(gameState, opponent1Pos, actions)
                        return action
                    else:
                        if(self.getMazeDistance(myPos, opponent1Pos)>=self.getMazeDistance(myPos, opponent2Pos)):
                            minDis, nearestDoor = self.getNearestTarget(gameState, opponent1Pos, self.behindBoundary)
                            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                            return action
                        else:
                            minDis, nearestDoor = self.getNearestTarget(gameState, opponent2Pos, self.behindBoundary)
                            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                            return action
                else:
                    if self.getMazeDistance(myPos, opponent2Pos) < self.pacmanHuntDistance:
                        self.lastKnownEnemyPacmanPosition = opponent2Pos
                        self.wantToGoAfterPacmanInHuntMode = True
                        minDis, action = self.getBestAction(gameState, opponent2Pos, actions)
                        return action
                    else:
                        if(self.getMazeDistance(myPos, opponent1Pos)>=self.getMazeDistance(myPos, opponent2Pos)):
                            minDis, nearestDoor = self.getNearestTarget(gameState, opponent1Pos, self.behindBoundary)
                            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                            return action
                        else:
                            minDis, nearestDoor = self.getNearestTarget(gameState, opponent2Pos, self.behindBoundary)
                            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                            return action
            elif opponent1 is not None or opponent2 is not None:
                currentOpponent = opponent1
                if(opponent1 is None):
                    currentOpponent  = opponent2
                else:
                    currentOpponent = opponent1

                currentOpponentPos = currentOpponent.getPosition()

                if self.getMazeDistance(myPos, currentOpponentPos) < self.pacmanHuntDistance:
                    if self.lastKnownEnemyPacmanPosition != currentOpponentPos:
                        self.lastKnownEnemyPacmanPosition = currentOpponentPos
                        self.wantToGoAfterPacmanInHuntMode = True
                    else:
                        self.wantToGoAfterPacmanInHuntMode = False
                    # self.wantToGoAfterPacmanInHuntMode = True
                    minDis, action = self.getBestAction(gameState, currentOpponentPos, actions)
                    return action
                else:
                    minDis, nearestDoor = self.getNearestTarget(gameState, currentOpponentPos, self.behindBoundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    return action

        elif len(opponentPacmans) == 1:
            opponent1 = opponentConfig[0]
            if opponent1 is not None:
                opponent1Pos = opponent1.getPosition()
                opponent1index = opponentPacmans[0]

                if self.getMazeDistance(myPos, opponent1Pos) < self.pacmanHuntDistance:
                    if self.lastKnownEnemyPacmanPosition != opponent1Pos:
                        self.lastKnownEnemyPacmanPosition = opponent1Pos
                        self.wantToGoAfterPacmanInHuntMode = True
                    else:
                        self.wantToGoAfterPacmanInHuntMode = False
                    minDis, action = self.getBestAction(gameState, opponent1Pos, actions)
                    return action
                else:
                    minDis, nearestDoor = self.getNearestTarget(gameState, opponent1Pos, self.behindBoundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    return action
        else:
            # no pacmans so we patrol spot
            # give constraint on x and go to patrol position with nearest ghost
            # check closest ghost

            self.wantToGoAfterPacmanInHuntMode = False

            opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
            opponentGhostsConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

            #print "ghost array" +str(opponentGhosts)
            #print "ghost config" +str(opponentGhostsConfig)
            #print "dadada" +gameState.getAgentState(1).configuration

            opponentGhost1 = opponentGhostsConfig[0]
            opponentGhost2 = opponentGhostsConfig[1]

            if opponentGhost1 is not None and opponentGhost2 is not None:

                opponentGhost1Pos = opponentGhost1.getPosition()
                opponentGhost2Pos = opponentGhost2.getPosition()

                if(self.getMazeDistance(myPos, opponentGhost1Pos)>=self.getMazeDistance(myPos, opponentGhost2Pos)):
                    # 1 is nearer
                    minDis, nearestDoor = self.getNearestTarget(gameState, opponentGhost1Pos, self.behindBoundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    return action
                else:
                    # 2 is nearer
                    minDis, nearestDoor = self.getNearestTarget(gameState, opponentGhost2Pos, self.behindBoundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    return action
            elif opponentGhost1 is not None or opponentGhost2 is not None:
                currentOpponent = opponentGhost1
                if(opponentGhost1 is None):
                    currentOpponent  = opponentGhost2
                else:
                    currentOpponent = opponentGhost1

                currentOpponentPos = currentOpponent.getPosition()
                minDis, nearestDoor = self.getNearestTarget(gameState, currentOpponentPos, self.behindBoundary)
                minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                return action
    else:
        # power pill has been used

        # stand at the best position for the pacman with most pills to cross the border

        # if we can kill it, kill it
        return Directions.STOP




    # we want to try to go to last known pacman position if we lose track of the ghosts
    if self.wantToGoAfterPacmanInHuntMode and not self.lastKnownEnemyPacmanPosition[0] >= self.boundary[0][0]:
        minDis, action = self.getBestAction(gameState, self.lastKnownEnemyPacmanPosition, actions)
        return action
    else:
        minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
        return action

    minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
    return action

  # returns distance to nearest target and the nearest target from an array by using maze distance
  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)

  # returns distance to furthest target and the furthest target from an array by using maze distance
  def getFurthestTarget(self, gameState, pos, targets):
    maxDisttoTarget, furthestTarget = max([(self.getMazeDistance(pos, target), target) for target in targets])
    return furthestTarget

  # returns getSuccessor but rounded to full positions
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
        return pos

  # returns best action by getting minimum distance from all actions
  def getBestAction(self, gameState, targetPos, actions):
    minDis, bestAction = min([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
    #print("best action", minDis, action)
    #print([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
    return (minDis, bestAction)

  # returns if at the door in between sides
  def isAtDoor(self, gameState):
    myPos = gameState.getAgentState(self.index).getPosition()
    if myPos in self.boundary:
        return True
    else:
        return False
