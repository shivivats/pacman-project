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
import distanceCalculator
import random
import time
import util
import sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
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

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

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


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.

    Attributes:
        deadEnds            All dead ends and their depth
        feasiblePositions   All positions in the field except walls (used for pre-calculations)
        passages            Passages through which pacman can move from its own field to enemy territory

    """

    GHOST_DISTANCE_THRESHOLD = 4
    SCARED_TIMER_THRESHOLD = 4
    SIMULATION_DEPTH = 3

    def __init__(self, index):
        CaptureAgent.__init__(self, index)
        # Variables used to verify if the agent os locked
        # self.numEnemyFood = "+inf"
        # self.inactiveTime = 0

        self.deadEnds = {}
        self.feasiblePositions = []
        self.passages = []

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

        self.initializeFeasiblePositions(gameState)

        self.initializeDeadEnds(gameState)

        self.initializePassages(gameState)

    def initializeFeasiblePositions(self, gameState):
        """
        Initialize all feasible positions on the field except walls
        """

        self.feasiblePositions = []
        for y in range(1, gameState.data.layout.height - 1):
            for x in range(1, gameState.data.layout.width - 1):
                if not gameState.hasWall(x, y):
                    self.feasiblePositions.append((x, y))

    def initializeDeadEnds(self, gameState):
        """
        Calculate all dead ends and their depth on the filed
        """

        self.deadEnds = {}

        # Contains all positions from which more than one way is possible
        crossings = util.Queue()

        # Initialize crossings
        # deadEndPosition = gameState.getAgentPosition(self.index)
        # deadEndDirection = gameState.getAgentState(self.index).configuration.direction
        actions = [action for action in gameState.getLegalActions(
            self.index) if action != Directions.STOP]

        for action in actions:
            crossings.push((gameState, action))

        # Repeat until all dead-ends have been found
        while not crossings.isEmpty():

            # Always start with a depth of 0
            # Generate the successor state for the action in the current crossing
            (state, action) = crossings.pop()
            depth = 0
            position = state.getAgentState(self.index).getPosition()
            currentState = state.generateSuccessor(self.index, action)

            # Repeat until a new crossing or a dead-end has been found
            # Follow a corridor
            while True:

                # Initialize agent position, its legal actions and directions of the successor state
                currentPosition = currentState.getAgentState(
                    self.index).getPosition()
                actions = [action for action in currentState.getLegalActions(
                    self.index) if action != Directions.STOP]
                currentDirection = currentState.getAgentState(
                    self.index).configuration.direction

                # Position has already been visited
                if currentPosition not in self.feasiblePositions:
                    break

                self.feasiblePositions.remove(currentPosition)

                # Remove the direction the agent is comming from
                if Directions.REVERSE[currentDirection] in actions:
                    actions.remove(Directions.REVERSE[currentDirection])

                # Dead-end reached
                if len(actions) == 0:
                    self.deadEnds[(position, action)] = depth + 1
                    break

                # Corridor, only one direction to move
                if len(actions) == 1:
                    depth += 1

                    # Generate successor state
                    currentState = currentState.generateSuccessor(
                        self.index, actions[0])
                # Crossing, more than two actions
                else:
                    for action in actions:
                        crossings.push((currentState, action))

                    break

    def initializePassages(self, gameState):
        """
        Initialize passages that connect the enemy field to our field
        """

        # Run the provided maze distance calculator
        self.distancer.getMazeDistances()

        # Width one players playfield without walls
        playfieldWidth = (gameState.data.layout.width - 2) / 2

        # x-coordinate that is adjacent to the enemies playfield but on our side
        centerX = playfieldWidth if self.red else playfieldWidth + 1

        # Initialize passages between own and enemy field
        self.passages = []
        for y in range(1, gameState.data.layout.height - 1):
            if not gameState.hasWall(centerX, y):
                self.passages.append((centerX, y))

    def getFeatures(self, gameState, action):
        """
        Get features used for state evaluation
        """

        features = util.Counter()

        # Compute score of successor for given action
        successorState = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(
            successorState) - self.getScore(gameState)

        # Compute distance to nearest food
        position = gameState.getAgentPosition(self.index)
        successorPosition = successorState.getAgentPosition(self.index)

        foodList = self.getFood(gameState).asList()
        if len(foodList) > 0:
            minimumDistance = min(
                [self.getMazeDistance(position, food) for food in foodList])
            minimumDistanceSucessor = min([self.getMazeDistance(
                successorPosition, food) for food in foodList])
            features['foodDistance'] = minimumDistance - \
                minimumDistanceSucessor

        features['deadEnds'] = 0

        # Compute weights for enemy ghosts, dead-ends and capsules
        opponents = [successorState.getAgentState(
            opponent) for opponent in self.getOpponents(successorState)]
        ghosts = [agent for agent in opponents if not agent.isPacman and agent.getPosition() != None and self.getMazeDistance(
            position, agent.getPosition()) <= OffensiveReflexAgent.GHOST_DISTANCE_THRESHOLD and agent.scaredTimer <= OffensiveReflexAgent.SCARED_TIMER_THRESHOLD]
        if len(ghosts) > 0:
            ghostPositions = [ghost.getPosition() for ghost in ghosts]
            closestGhost = min(ghostPositions, key=lambda ghostPosition: self.getMazeDistance(
                position, ghostPosition))

            ghostDistance = self.getMazeDistance(position, closestGhost)
            ghostDistanceSuccessor = self.getMazeDistance(
                successorPosition, closestGhost)

            # Pacman would get trapped in a dead-end
            if self.deadEnds.has_key((position, action)) and self.deadEnds[(position, action)] * 2 > ghostDistance:
                features['deadEnds'] = 1

            elif ghostDistance < OffensiveReflexAgent.GHOST_DISTANCE_THRESHOLD:

                runawayDistance = ghostDistanceSuccessor - ghostDistance

                # Pacman has been eaten (random higher number)
                if runawayDistance > 5:
                    features['ghostDistance'] = -100
                else:
                    features['ghostDistance'] = runawayDistance

                # Calculate distance to capsules
                capsules = self.getCapsules(gameState)
                if len(capsules) > 0:
                    pass
                    minimumCapsule = min([self.getMazeDistance(
                        position, capsule) for capsule in capsules])
                    minimumCapsuleSuccessor = min([self.getMazeDistance(
                        successorPosition, capsule) for capsule in capsules])
                    features['capsuleDistance'] = minimumCapsule - \
                        minimumCapsuleSuccessor
                else:
                    features['capsuleDistance'] = 0

        # Compute distance to closest passage
        passageMinimum = float("+inf")

        for i in range(len(self.passages)):
            passageDistance = self.getMazeDistance(position, self.passages[i])

            if passageDistance < passageMinimum:
                passageMinimum = passageDistance

        features['returned'] = passageMinimum
        features['carrying'] = successorState.getAgentState(
            self.index).numCarrying

        return features

    def getWeights(self, gameState, action):
        """
        Get weights for each feature used in the evaluation.
        This normally does not depend on the action nor game state
        """

        return {
            'successorScore': 500,
            'foodDistance': 20,
            'ghostDistance': 500,
            'capsuleDistance': 300,
            'deadEnds': -2000,
            'returned': 0,
            'carrying': 0
        }

    def simulateAction(self, depth, gameState, decay):
        """
        Simulate actions and determine the best result
        """

        stateCopy = gameState.deepCopy()

        actions = [action for action in stateCopy.getLegalActions(
            self.index) if action != Directions.STOP]

        if depth == 0:
            return max([self.evaluate(stateCopy, action) for action in actions])

        result = []
        for action in actions:
            successorState = stateCopy.generateSuccessor(self.index, action)
            result.append(self.evaluate(stateCopy, action) + decay *
                          self.simulateAction(depth - 1, successorState, decay))

        return max(result)

    def chooseAction(self, gameState):
        """
        Chose the best action
        """

        actions = [action for action in gameState.getLegalActions(
            self.index) if action != Directions.STOP]

        # Calculate scores for each action
        values = []
        for action in actions:
            successorState = gameState.generateSuccessor(self.index, action)
            value = self.evaluate(gameState, action)
            value += self.simulateAction(
                OffensiveReflexAgent.SIMULATION_DEPTH, successorState, 0.5)
            values.append(value)

        # Determine the best action
        bestValue = max(values)
        bestActions = filter(lambda x: x[0] == bestValue, zip(values, actions))
        return random.choice(bestActions)[1]


class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free.

    This agent will patrol POIs on our own side (POI = spots where an emeny may invade)
    It will chase after an invading enemey
    If no enemey has been spotted but food still has disappeared, it will head this area
    If there is only a few food left (FOOD_THRESHOLD), it will try to defend the remaining food

    Attributes:
        pois                Points of interests on our side of the field: spots where an enemy pacman may invade
        poiProbabilities    Probability for each point of interest (updated each time)
        lastObservedFood    Food on our side in the previous game state
        target              The agent will go to this position
    """
    FOOD_THRESHOLD = 4

    def __init__(self, index):
        CaptureAgent.__init__(self, index)

        self.pois = []
        self.poiProbabilities = {}
        self.lastObservedFood = None
        self.target = None

    def registerInitialState(self, gameState):
        """
        Initialize points of interest
        """
        CaptureAgent.registerInitialState(self, gameState)

        # Run the provided maze distance calculator
        self.distancer.getMazeDistances()

        # Width one players playfield without walls
        playfieldWidth = (gameState.data.layout.width - 2) / 2

        # x-coordinate that is adjacent to the enemies playfield but on our side
        centerX = playfieldWidth if self.red else playfieldWidth + 1

        # Compute possible position for an enemy pacman to invade
        self.pois = []

        for i in range(1, gameState.data.layout.height - 1):
            if not gameState.hasWall(centerX, i):
                self.pois.append((centerX, i))

        # Remove upper and lower positions to reduce pois
        # This will force the defender to stay central
        poiThreshold = (gameState.data.layout.height - 2) / 2

        while len(self.pois) > poiThreshold:
            self.pois.pop(0)
            self.pois.pop(len(self.pois) - 1)

        # Update probabilities to each patrol point.
        self.updatePoiProbabilities(gameState)

    def updatePoiProbabilities(self, gameState):
        """
        Calculate distances to the closest food for each POI.
        The POI with the closest distances will be selected as the next patrol point.
        """

        foodList = self.getFoodYouAreDefending(gameState).asList()
        total = 0

        for poi in self.pois:
            closestDistance = float("+inf")

            # Find the smallest distance to food
            for food in foodList:
                distanceToFood = self.getMazeDistance(poi, food)

                if distanceToFood < closestDistance:
                    closestDistance = distanceToFood

            if closestDistance == 0:
                closestDistance = 1

            # Invert
            inverted = 1.0 / closestDistance
            self.poiProbabilities[poi] = inverted

            total += inverted

        if total == 0:
            total = 1

        # Normalize values
        for poi in self.poiProbabilities.keys():
            self.poiProbabilities[poi] = float(
                self.poiProbabilities[poi]) / float(total)

    def selectPoi(self):
        """
        Select the next POI for patroling based on the caclulated propabilities
        """

        rand = random.random()
        randSum = 0.0

        for poi in self.poiProbabilities.keys():
            randSum += self.poiProbabilities[poi]
            if rand < randSum:
                return poi

    def chooseAction(self, gameState):
        """
        Determine the agents next action:
            Enemy in sight: Chase enemy
            No enemy in sight and no dots eaten: Go to a POI
            No enemy in sight, no dots eaten but only few dots left: Go to remaining dots
            No enemy in sight but dots eaten: Go to position where dots disappeared
        """

        foodToDefend = self.getFoodYouAreDefending(gameState).asList()

        # Food was eaten in the previous game state --> Update POI probabilities
        if self.lastObservedFood and len(self.lastObservedFood) != foodToDefend:
            self.updatePoiProbabilities(gameState)

        agentPosition = gameState.getAgentPosition(self.index)

        # Reset target if the agend has reached it
        if agentPosition == self.target:
            self.target = None

        opponents = [gameState.getAgentState(
            opponent) for opponent in self.getOpponents(gameState)]
        invaders = [
            invader for invader in opponents if invader.isPacman and invader.getPosition() != None]

        # Invader found: chase after the closest invader
        if len(invaders) > 0:
            invaderPositions = [invader.getPosition() for invader in invaders]
            self.target = min(invaderPositions, key=lambda position: self.getMazeDistance(
                agentPosition, position))
        # No invader found, check if food has been eaten in the previous state
        elif self.lastObservedFood != None:
            eatenFood = set(self.lastObservedFood) - set(foodToDefend)

            # Food has been eaten, go to its position
            if len(eatenFood) > 0:
                self.target = eatenFood.pop()

        # Update last observed food
        self.lastObservedFood = foodToDefend

        # No food has been eaten and no enemy in sight
        # Only few food is remaining
        if self.target == None and len(foodToDefend) <= DefensiveReflexAgent.FOOD_THRESHOLD:
            remainingFood = foodToDefend + \
                self.getCapsulesYouAreDefending(gameState)
            self.target = random.choice(remainingFood)
        # No action going on, select next POI
        elif self.target == None:
            self.target = self.selectPoi()

        # Finally, take the action that gets the agent closer to the target
        # The agent will
        # - never stop
        # - never invade enemy territory

        legalActions = [action for action in gameState.getLegalActions(
            self.index) if action != Directions.STOP]
        actions = []
        actionDistances = []

        for action in legalActions:
            successor = gameState.generateSuccessor(self.index, action)

            # Agent stays on our side
            if not successor.getAgentState(self.index).isPacman:
                actions.append(action)
                actionDistances.append(self.getMazeDistance(
                    successor.getAgentPosition(self.index), self.target))

        # Find the best action (closest distance to target) and select randomly among ties
        bestDistance = min(actionDistances)
        bestActions = filter(
            lambda x: x[0] == bestDistance, zip(actionDistances, actions))
        return random.choice(bestActions)[1]
