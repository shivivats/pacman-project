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
               first = 'Attacker', second = 'Defender'):
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

    # if more than 2 foods
    if len(foods) > 2:

        scaredTimes = [gameState.getAgentState(i).scaredTimer for i in self.opponent]

        opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

        if len(opponentGhosts) == 2:
            #print("2")
            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]

            # if we have both opponents and both are scared <5 seconds
            if opponent1 is not None and opponent2 is not None and (scaredTimes[0] <= 5 or scaredTimes[1] <= 5):

                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()

                if len(capsules) > 0:
                # capsules is the opponent side's capsules

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    # if capsule is closer than opponent, go to capsule
                    if distToCap < self.getMazeDistance(opponent1Pos, nearestCapsule) & distToCap < self.getMazeDistance(opponent2Pos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # check if we're within 5 distance of opponent
                if self.getMazeDistance(myPos, opponent1Pos) <= 5 or self.getMazeDistance(myPos, opponent1Pos) <= 5:

                    # if we're within 5 distance of an opponent, and we're pacman, go to the nearest door
                    if gameState.getAgentState(self.index).isPacman:
                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c", "door", nearestDoor, minDis)
                        return action


                    else:
                        # if we're within 5 distance, and we're not pacman, and parner is less than 10 distance away, then chase nearest food
                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z", "suiside", nearestFood, minDis)
                                return action

                        # if we're within 5 distance, and we're not pacman, and we're already at door and we arent chasing random food, then chase random food
                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b", "randfood", self.randFood, minDis)
                            return action

                        # if we're within 5 distance, and we're not pacman, and not chasing random food, then chase random food i guess
                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action

        # else if we only have 1 ghost
        elif len(opponentGhosts) == 1:
            #print("1")
            opponent = opponentConfig[0]
            if opponent is not None and gameState.getAgentState(opponentGhosts[0]).scaredTimer <= 5:

                opponentPos = opponent.getPosition()

                if len(capsules) > 0:
                # capsules is the opponent side's capsules

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    # if capsule is closer than opponent, go to capsule
                    if distToCap < self.getMazeDistance(opponentPos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # if we're within 5 of opponent
                if self.getMazeDistance(myPos, opponentPos) <= 5:

                    # if we're within 5 of opponent and we're pacman, go to nearest door
                    if gameState.getAgentState(self.index).isPacman:

                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c-2", "door", nearestDoor, minDis)
                        return action

                    # if we're within 5 of opponent and we're not pacman
                    else:

                        # if we're within 5 of opponent and we're not pacman, and we're less than 10 from partner, go to nearest food
                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z-2", "suiside", nearestFood, minDis)
                                return action

                        # if we're within 5 of opponent and we're not pacman, and we're at a door and not chasing random food, chase random food
                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-1", "randfood", self.randFood, minDis)
                            return action

                        # if we're within 5 of opponent and we're not pacman, and we're not chasing random food, chase random food
                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action

        # if we dont have any ghosts, and we're chasing random foods (?) then chase random food and decrease random food count by 1
        if self.randFoodStatus > 0:
            minDis, action = self.getBestAction(gameState, self.randFood, actions)
            self.randFoodStatus -= 1
            #print(self.index, "countdown", self.randFood, minDis, self.randFoodStatus)
            return action

        # partner's distance to food, our distance to food, and our distance to door
        partnerMinDisttoFood, partnerNearestFood = self.getNearestTarget(gameState, partnerPos, foods)
        myMinDisttoFood, myNearestFood = self.getNearestTarget(gameState, myPos, foods)
        minDisttoHome, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)

        # if number of dots we're carrying is more than the distance to the other side, go to the nearest door
        if gameState.getAgentState(self.index).numCarrying > minDisttoHome:
            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
            #print(self.index, "g", "door", nearestDoor, minDis)
            return action

        # if we and partner are both nearest to the same food
        if myNearestFood == partnerNearestFood:

            # if we're closer to the food, its the nearest food
            if myMinDisttoFood < partnerMinDisttoFood:
                self.nearestFood = myNearestFood
            # if we and partner are both equal distance from food, if we're the first one in the team
            # and our distance to food is less or equal to minimum distance, set nearestFood to furthestTarget(?)
            elif myMinDisttoFood == partnerMinDisttoFood:
                if self.index == self.team[0]:
                    if self.getMazeDistance(myPos, self.nearestFood) <= myMinDisttoFood:
                        self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
                else:
                    # if we're not the first then set nearestfood to our nearest food
                    self.nearestFood = myNearestFood
            else:
                # if partner is closet to foods
                # and our nearest food is that, we set the nearestfood to furthest food
                if self.nearestFood == myNearestFood:
                    self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
        else:
            # we and partner are not closest to the same food, so we go to our nearest food
            self.nearestFood = myNearestFood

        minDis, action = self.getBestAction(gameState, self.nearestFood, actions)
        #print(self.index, "h", "food", self.nearestFood, minDis)
        return action

    # if less than or equal to 2 dots left, just run to nearest door
    else:
        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
        #print(self.index, "i", "door", nearestDoor, minDis)
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

    # if more than 2 foods
    if len(foods) > 2:

        scaredTimes = [gameState.getAgentState(i).scaredTimer for i in self.opponent]

        opponentGhosts = [i for i in self.opponent if not gameState.getAgentState(i).isPacman]
        opponentConfig = [gameState.getAgentState(i).configuration for i in opponentGhosts]

        if len(opponentGhosts) == 2:
            #print("2")
            opponent1 = opponentConfig[0]
            opponent2 = opponentConfig[1]

            # if we have both opponents and both are scared <5 seconds
            if opponent1 is not None and opponent2 is not None and (scaredTimes[0] <= 5 or scaredTimes[1] <= 5):

                opponent1Pos = opponent1.getPosition()
                opponent2Pos = opponent2.getPosition()

                if len(capsules) > 0:
                # capsules is the opponent side's capsules

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    # if capsule is closer than opponent, go to capsule
                    if distToCap < self.getMazeDistance(opponent1Pos, nearestCapsule) & distToCap < self.getMazeDistance(opponent2Pos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # check if we're within 5 distance of opponent
                if self.getMazeDistance(myPos, opponent1Pos) <= 5 or self.getMazeDistance(myPos, opponent1Pos) <= 5:

                    # if we're within 5 distance of an opponent, and we're pacman, go to the nearest door
                    if gameState.getAgentState(self.index).isPacman:
                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c", "door", nearestDoor, minDis)
                        return action


                    else:
                        # if we're within 5 distance, and we're not pacman, and parner is less than 10 distance away, then chase nearest food
                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z", "suiside", nearestFood, minDis)
                                return action

                        # if we're within 5 distance, and we're not pacman, and we're already at door and we arent chasing random food, then chase random food
                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b", "randfood", self.randFood, minDis)
                            return action

                        # if we're within 5 distance, and we're not pacman, and not chasing random food, then chase random food i guess
                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action

        # else if we only have 1 ghost
        elif len(opponentGhosts) == 1:
            #print("1")
            opponent = opponentConfig[0]
            if opponent is not None and gameState.getAgentState(opponentGhosts[0]).scaredTimer <= 5:

                opponentPos = opponent.getPosition()

                if len(capsules) > 0:
                # capsules is the opponent side's capsules

                    distToCap, nearestCapsule = self.getNearestTarget(gameState, myPos, capsules)

                    # if capsule is closer than opponent, go to capsule
                    if distToCap < self.getMazeDistance(opponentPos, nearestCapsule):
                        minDis, action = self.getBestAction(gameState, nearestCapsule, actions)
                        #print(self.index, "a", "cap", nearestCapsule, minDis)
                        return action

                # if we're within 5 of opponent
                if self.getMazeDistance(myPos, opponentPos) <= 5:

                    # if we're within 5 of opponent and we're pacman, go to nearest door
                    if gameState.getAgentState(self.index).isPacman:

                        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
                        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
                        #print(self.index, "c-2", "door", nearestDoor, minDis)
                        return action

                    # if we're within 5 of opponent and we're not pacman
                    else:

                        # if we're within 5 of opponent and we're not pacman, and we're less than 10 from partner, go to nearest food
                        if self.getMazeDistance(myPos, partnerPos) <= 10:
                            if self.index == self.team[0]:
                                minDis, nearestFood = self.getNearestTarget(gameState, myPos, foods)
                                minDis, action = self.getBestAction(gameState, nearestFood, actions)
                                #print(self.index, "z-2", "suiside", nearestFood, minDis)
                                return action

                        # if we're within 5 of opponent and we're not pacman, and we're at a door and not chasing random food, chase random food
                        if self.isAtDoor(gameState) and self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-1", "randfood", self.randFood, minDis)
                            return action

                        # if we're within 5 of opponent and we're not pacman, and we're not chasing random food, chase random food
                        if self.randFoodStatus == 0:
                            if len(self.getFoodYouAreDefending(gameState).asList()) > 0:
                                self.randFood = random.choice(self.getFoodYouAreDefending(gameState).asList())
                            minDis, action = self.getBestAction(gameState, self.randFood, actions)
                            self.randFoodStatus = 6
                            #print(self.index, "b-2", "randfood", self.randFood, minDis)
                            return action

        # if we dont have any ghosts, and we're chasing random foods (?) then chase random food and decrease random food count by 1
        if self.randFoodStatus > 0:
            minDis, action = self.getBestAction(gameState, self.randFood, actions)
            self.randFoodStatus -= 1
            #print(self.index, "countdown", self.randFood, minDis, self.randFoodStatus)
            return action

        # partner's distance to food, our distance to food, and our distance to door
        partnerMinDisttoFood, partnerNearestFood = self.getNearestTarget(gameState, partnerPos, foods)
        myMinDisttoFood, myNearestFood = self.getNearestTarget(gameState, myPos, foods)
        minDisttoHome, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)

        # if number of dots we're carrying is more than the distance to the other side, go to the nearest door
        if gameState.getAgentState(self.index).numCarrying > minDisttoHome:
            minDis, action = self.getBestAction(gameState, nearestDoor, actions)
            #print(self.index, "g", "door", nearestDoor, minDis)
            return action

        # if we and partner are both nearest to the same food
        if myNearestFood == partnerNearestFood:

            # if we're closer to the food, its the nearest food
            if myMinDisttoFood < partnerMinDisttoFood:
                self.nearestFood = myNearestFood
            # if we and partner are both equal distance from food, if we're the first one in the team
            # and our distance to food is less or equal to minimum distance, set nearestFood to furthestTarget(?)
            elif myMinDisttoFood == partnerMinDisttoFood:
                if self.index == self.team[0]:
                    if self.getMazeDistance(myPos, self.nearestFood) <= myMinDisttoFood:
                        self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
                else:
                    # if we're not the first then set nearestfood to our nearest food
                    self.nearestFood = myNearestFood
            else:
                # if partner is closet to foods
                # and our nearest food is that, we set the nearestfood to furthest food
                if self.nearestFood == myNearestFood:
                    self.nearestFood = self.getFurthestTarget(gameState, myPos, foods)
        else:
            # we and partner are not closest to the same food, so we go to our nearest food
            self.nearestFood = myNearestFood

        minDis, action = self.getBestAction(gameState, self.nearestFood, actions)
        #print(self.index, "h", "food", self.nearestFood, minDis)
        return action

    # if less than or equal to 2 dots left, just run to nearest door
    else:
        minDis, nearestDoor = self.getNearestTarget(gameState, myPos, self.boundary)
        minDis, action = self.getBestAction(gameState, nearestDoor, actions)
        #print(self.index, "i", "door", nearestDoor, minDis)
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
