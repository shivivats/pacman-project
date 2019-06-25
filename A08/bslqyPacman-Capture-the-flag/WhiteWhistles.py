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
               first = 'Lyza', second = 'Ozen'):
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

global lyzaDefenseMode
global ozenDefenseMode

class Lyza(CaptureAgent):
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

    ''' offensive agent '''
    self.initialTarget = None
    self.ourOldPacmanCount = 1
    self.ownTeam = self.getTeam(gameState)
    self.haveAdvantage = False

    ''' defensive agent '''
    self.nearestBoundary = (1,1)
    self.powerPillUsed=False
    self.currentBoundaryIndex=0
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
    self.powerPillCount = 1

    ''' common agent stuff '''
    self.amIDefending = False
    self.superDefenseBoundary = []
    if self.red:
        centralBehindX = (gameState.data.layout.width - 2) / 2 -2
    else:
        centralBehindX = ((gameState.data.layout.width - 2) / 2) + 1 + 2
    for i in range(1, gameState.data.layout.height/2):
        if not gameState.hasWall(centralBehindX, i):
            self.superDefenseBoundary.append((centralBehindX, i))
    self.bothGhosts = 2

    print str(self.superDefenseBoundary)

    self.superDefenseMode = True


  def chooseAction(self, gameState):
    """
    Semi-greedy agent.
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

    ''' offensive agent initial stuff'''
    ourPacmans = [i for i in self.ownTeam if gameState.getAgentState(i).isPacman]
    if self.getScore(gameState) > 3:
        self.haveAdvantage = True
    else:
        self.haveAdvantage = False
    # if the furthest food from this agent is not in the food list?, then get nearest food?
    if self.nearestFood not in foods:
        minDis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)

    ''' defensive initial stuff '''
    defendFood = self.getFoodYouAreDefending(gameState).asList()
    minBoundaryDistance, self.nearestBoundary = self.getNearestTarget(gameState, myPos, self.boundary)
    if self.nearestFood not in foods:
        mindis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)
    # ghost loses configuration hence he stops going after them so implement furthestTarget
    # can also decrease the distance threshold to pacman for kill tomorrow
    if self.powerPillCount == 0:
        self.powerPillUsed = True
    #print str(self.powerPillUsed) + "," + str(self.powerPillCount)
    # if less than 2 foods, go into super hunt mode
    if len(defendFood) <= 5:
        self.pacmanHuntDistance = 50

    ''' common initial stuff '''
    ourGhosts = [i for i in self.ownTeam if not gameState.getAgentState(i).isPacman]
    self.bothGhosts = len(ourGhosts)

    if self.powerPillUsed and gameState.getAgentState(self.index).scaredTimer > 10:
        self.superDefenseMode=False

    if (len(foods) <= 3 and self.getScore(gameState)>=0) or self.haveAdvantage:
        self.superDefenseMode = True



    # if we have more than 3 food left and not advantage we attack
    if len(foods) > 4 and not self.haveAdvantage:

        lyzaDefenseMode = False

        scaredTimes = [gameState.getAgentState(i).scaredTimer for i in self.opponent]
        opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

        #
        if len(opponentGhosts) == 2:
            #print("2")
            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]

            # if we detect both opponents and their scared timers are less than 5
            if opponent1 is not None and opponent2 is not None:
                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()

                # if we have 2 ghosts and there is pill, then go for pill
                if len(capsules) > 0:
                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)
                    if distToCap < self.getMazeDistance(opponent1Pos, nearestCapsule) & distToCap < self.getMazeDistance(opponent2Pos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action


                # if we're within 3 distance of any ghost, we run to the boundary
                if self.getMazeDistance(myPos, opponent1Pos) <= 3 or self.getMazeDistance(myPos, opponent2Pos) <= 3:
                    minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    #print(self.index, "c", "door", nearestDoor, minDis)
                    return action

            # if we only detect one opponent we only try to avoid that one
            #elif opponent1 is not None or opponent2 is not None and (scaredTimes[0] <= 5 or scaredTimes[1] <= 5):


        #
        elif len(opponentGhosts) == 1:
            #print("1")
            opponent = opponentConfig[0]

            if opponent is not None:
                opponentPos = opponent.getPosition()

                # if we have capsule and enemy ghost is not closer to capsule
                if len(capsules) > 0:
                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)
                    if distToCap < self.getMazeDistance(opponentPos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # run towards the boundary
                if self.getMazeDistance(myPos, opponentPos) <= 3:
                    minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    #print(self.index, "c-2", "door", nearestDoor, minDis)
                    return action
                    # no else cause we dont care if we're not pacman right now

        else:
            if self.red:
                if gameState.getAgentState(self.index).getPosition()[0] > self.boundary[0][0]: # change this to work with blue as well
                    # check if you have dots
                    # if you do, run back
                    if gameState.getAgentState(self.index).numCarrying > 0:
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "g", "door", nearestDoor, minDis)
                        return action
            else:
                if gameState.getAgentState(self.index).getPosition()[0] < self.boundary[0][0]: # change this to work with blue as well
                    # check if you have dots
                    # if you do, run back
                    if gameState.getAgentState(self.index).numCarrying > 0:
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "g", "door", nearestDoor, minDis)
                        return action

        # idle code, when no opponents are found
        minDisttoHome, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)

        # go to home if you are carrying a lotta dots
        percentCarrying = float(gameState.getAgentState(self.index).numCarrying) / float(len(self.getFood(gameState).asList()))
        if percentCarrying >= 0.1 :
            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
            #print(self.index, "g", "door", nearestDoor, minDis)
            return action


        myMinDisttoFood, myNearestFood = self.getNearestTarget(gameState, myPos, foods)
        myMinDisttoSecondFood, mySecondNearestFood = self.getSecondNearestTarget(gameState, myPos, foods)
        self.nearestFood = myNearestFood

        #no need to change for blue bc not used
        #if self.initialTarget is None and gameState.getAgentState(self.index).getPosition()[0] < self.boundary[0][0]:
        if len(ourPacmans) < self.ourOldPacmanCount:
            self.initialTarget = random.choice(foods)

        self.ourOldPacmanCount = len(ourPacmans)

        #print "initial target " +str(self.initialTarget)

        if self.initialTarget is not None:
            if gameState.getAgentState(self.index).getPosition() == self.initialTarget:
                # and we update initialtarget
                self.initialTarget = None
            else:
                minDis, action = self.getBestAction(gameState, self.initialTarget, actions)
                return action

        minDis, action = self.getBestAction(gameState, self.nearestFood, actions)
        #print(self.index, "h", "food", self.nearestFood, minDis)
        return action

    # if we have 2 or less foods remaining

    # if we have less than 3 food left or advantage we defend
    else:

        #print "defensive mode for lyza"

        #  do something

        lyzaDefenseMode = True

        print "lyza defense mode"

        opponentPacmans = [i for i in self.opponent if gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentPacmans]

        #print "pacman config" +str(opponentConfig)

        # if the opponent has 2 pacmans
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


        # we want to try to go to last known pacman position if we lose track of the ghosts change for blue
        if self.red:
            if self.wantToGoAfterPacmanInHuntMode and not self.lastKnownEnemyPacmanPosition[0] >= self.boundary[0][0]:
                minDis, action = self.getBestAction(gameState, self.lastKnownEnemyPacmanPosition, actions)
                return action
            else:
                if self.bothGhosts == 2 and self.superDefenseMode:
                    print "super defense"
                    minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
                else:
                    #print "regular defense"
                    #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
                    minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
                return action
        else:
            if self.wantToGoAfterPacmanInHuntMode and not self.lastKnownEnemyPacmanPosition[0] <= self.boundary[0][0]:
                minDis, action = self.getBestAction(gameState, self.lastKnownEnemyPacmanPosition, actions)
                return action
            else:
                if self.bothGhosts == 2 and self.superDefenseMode:
                    print "super defense"
                    minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
                else:
                    #print "regular defense"
                    #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
                    minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
                return action

        if self.bothGhosts == 2 and self.superDefenseMode:
            print "super defense"
            minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
        else:
            #print "regular defense"
            #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
            minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
        return action


  '''
    Helper Functionss
  '''
  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)

  def getSecondNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    targets.remove(nearestTarget)
    minDis, secondNearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, secondNearestTarget)

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


class Ozen(CaptureAgent):
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

    ''' defensive agent '''
    self.nearestBoundary = (1,1)
    self.powerPillUsed=False
    self.currentBoundaryIndex=0
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
    self.powerPillCount = 1

    ''' offensive agent '''
    self.initialTarget = None
    self.ourOldPacmanCount = 1
    self.ownTeam = self.getTeam(gameState)
    self.haveAdvantage = False

    ''' common agent stuff '''
    self.amIDefending = False
    self.superDefenseBoundary = []
    if self.red:
        centralBehindX = (gameState.data.layout.width - 2) / 2 -2
    else:
        centralBehindX = ((gameState.data.layout.width - 2) / 2) + 1 + 2
    for i in range(gameState.data.layout.height/2, gameState.data.layout.height - 1):
        if not gameState.hasWall(centralBehindX, i):
            self.superDefenseBoundary.append((centralBehindX, i))

    print str(self.superDefenseBoundary)
    print str(gameState.data.layout.width)
    print str(gameState.data.layout.height)
    print str(gameState.hasWall(0, 0))
    self.bothGhosts = 2
    self.superDefenseMode=False


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
        self.powerPillCount =  len(gameState.getRedCapsules())
    else:
        capsules = gameState.getRedCapsules()
        self.powerPillCount =  len(gameState.getBlueCapsules())

    foods += capsules
    defendFood = self.getFoodYouAreDefending(gameState).asList()
    partnerPos = gameState.getAgentState(self.partnerIndex).getPosition()

    ''' defensive initial stuff '''
    minBoundaryDistance, self.nearestBoundary = self.getNearestTarget(gameState, myPos, self.boundary)
    if self.nearestFood not in foods:
        mindis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)
    # ghost loses configuration hence he stops going after them so implement furthestTarget
    # can also decrease the distance threshold to pacman for kill tomorrow
    if self.powerPillCount == 0:
        self.powerPillUsed = True
    #print str(self.powerPillUsed) + "," + str(self.powerPillCount)
    # if less than 2 foods, go into super hunt mode
    if len(defendFood) <= 5:
        self.pacmanHuntDistance = 50

    ''' offensive agent initial stuff'''
    ourPacmans = [i for i in self.ownTeam if gameState.getAgentState(i).isPacman]
    if self.getScore(gameState) > 3:
        self.haveAdvantage = True
    else:
        self.haveAdvantage = False
    # if the furthest food from this agent is not in the food list?, then get nearest food?
    if self.nearestFood not in foods:
        minDis, self.nearestFood = self.getNearestTarget(gameState, myPos, foods)

    ''' common initial stuff '''
    ourGhosts = [i for i in self.ownTeam if not gameState.getAgentState(i).isPacman]
    self.bothGhosts = len(ourGhosts)


    if len(foods) <= 3 or self.haveAdvantage:
        self.superDefenseMode=True

    # if more than 2 foods
    if self.powerPillUsed and gameState.getAgentState(self.index).scaredTimer > 10:
        # power pill has been used

        # go into agressive mode

        #print "offensive mode for ozen"

        ozenDefenseMode = False

        print "ozen offense mode"

        scaredTimes = [gameState.getAgentState(i).scaredTimer for i in self.opponent]
        opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

        #
        if len(opponentGhosts) == 2:
            #print("2")
            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]

            # if we detect both opponents and their scared timers are less than 5
            if opponent1 is not None and opponent2 is not None:
                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()

                # if we have 2 ghosts and there is pill, then go for pill
                if len(capsules) > 0:
                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)
                    if distToCap < self.getMazeDistance(opponent1Pos, nearestCapsule) & distToCap < self.getMazeDistance(opponent2Pos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action


                # if we're within 3 distance of any ghost, we run to the boundary
                if self.getMazeDistance(myPos, opponent1Pos) <= 3 or self.getMazeDistance(myPos, opponent2Pos) <= 3:
                    minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    #print(self.index, "c", "door", nearestDoor, minDis)
                    return action

            # if we only detect one opponent we only try to avoid that one
            #elif opponent1 is not None or opponent2 is not None and (scaredTimes[0] <= 5 or scaredTimes[1] <= 5):


        #
        elif len(opponentGhosts) == 1:
            #print("1")
            opponent = opponentConfig[0]

            if opponent is not None:
                opponentPos = opponent.getPosition()

                # if we have capsule and enemy ghost is not closer to capsule
                if len(capsules) > 0:
                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)
                    if distToCap < self.getMazeDistance(opponentPos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # run towards the boundary
                if self.getMazeDistance(myPos, opponentPos) <= 3:
                    minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                    minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                    #print(self.index, "c-2", "door", nearestDoor, minDis)
                    return action
                    # no else cause we dont care if we're not pacman right now

        else:
            if self.red:
                if gameState.getAgentState(self.index).getPosition()[0] > self.boundary[0][0]: # change this to work with blue as well
                    # check if you have dots
                    # if you do, run back
                    if gameState.getAgentState(self.index).numCarrying > 0:
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "g", "door", nearestDoor, minDis)
                        return action
            else:
                if gameState.getAgentState(self.index).getPosition()[0] < self.boundary[0][0]: # change this to work with blue as well
                    # check if you have dots
                    # if you do, run back
                    if gameState.getAgentState(self.index).numCarrying > 0:
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "g", "door", nearestDoor, minDis)
                        return action

        # idle code, when no opponents are found
        minDisttoHome, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)

        # go to home if you are carrying a lotta dots
        percentCarrying = float(gameState.getAgentState(self.index).numCarrying) / float(len(self.getFood(gameState).asList()))
        if percentCarrying >= 0.1 :
            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
            #print(self.index, "g", "door", nearestDoor, minDis)
            return action


        myMinDisttoFood, myNearestFood = self.getNearestTarget(gameState, myPos, foods)
        myMinDisttoSecondFood, mySecondNearestFood = self.getSecondNearestTarget(gameState, myPos, foods)
        self.nearestFood = myNearestFood

        #no need to change for blue bc not used
        #if self.initialTarget is None and gameState.getAgentState(self.index).getPosition()[0] < self.boundary[0][0]:
        if len(ourPacmans) < self.ourOldPacmanCount:
            self.initialTarget = random.choice(foods)

        self.ourOldPacmanCount = len(ourPacmans)

        #print "initial target " +str(self.initialTarget)

        if self.initialTarget is not None:
            if gameState.getAgentState(self.index).getPosition() == self.initialTarget:
                # and we update initialtarget
                self.initialTarget = None
            else:
                minDis, action = self.getBestAction(gameState, self.initialTarget, actions)
                return action

        minDis, action = self.getBestAction(gameState, self.nearestFood, actions)
        #print(self.index, "h", "food", self.nearestFood, minDis)
        return action


    # defensive code

    else:

        #  do something

        ozenDefenseMode = True

        #self.amIDefending = True

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


        # we want to try to go to last known pacman position if we lose track of the ghosts change for blue



        if self.red:
            if self.wantToGoAfterPacmanInHuntMode and not self.lastKnownEnemyPacmanPosition[0] >= self.boundary[0][0]:
                minDis, action = self.getBestAction(gameState, self.lastKnownEnemyPacmanPosition, actions)
                return action
            else:
                if self.bothGhosts == 2 and self.superDefenseMode:
                    print "super defense"
                    minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
                else:
                    #print "regular defense"
                    #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
                    minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
                return action
        else:
            if self.wantToGoAfterPacmanInHuntMode and not self.lastKnownEnemyPacmanPosition[0] <= self.boundary[0][0]:
                minDis, action = self.getBestAction(gameState, self.lastKnownEnemyPacmanPosition, actions)
                return action
            else:
                if self.bothGhosts == 2 and self.superDefenseMode:
                    print "super defense"
                    minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
                else:
                    #print "regular defense"
                    #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
                    minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
                return action

        if self.bothGhosts == 2 and self.superDefenseMode:
            print "super defense"
            minDis, action = self.getBestAction(gameState, random.choice(self.superDefenseBoundary), actions)
        else:
            #print "regular defense"
            #print "lyzadef "+str(lyzaDefenseMode) + "ozendef "+str(ozenDefenseMode) + "bothghosts "+str(self.bothGhosts)
            minDis, action = self.getBestAction(gameState, random.choice(self.behindBoundary), actions)
        return action

  ''' helper functions '''
  # returns distance to nearest target and the nearest target from an array by using maze distance
  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)

  def getSecondNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    targets.remove(nearestTarget)
    minDis, secondNearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, secondNearestTarget)

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
