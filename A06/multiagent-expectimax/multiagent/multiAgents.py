# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

import math

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        """
        score, move = self.minimax(0, gameState, 0, True)
        return move
        """

        # if getLegalActions only has 1 member then return that anyways
        # only use evaluation function when the game is over


        pacmanScoreList, pacmanMoveList = self.minimax(gameState, 0, self.depth)

        bestAction = pacmanMoveList[pacmanScoreList.index(max(pacmanScoreList))]
        return bestAction
        util.raiseNotDefined()

        """
        scoreList = []
        moveList = []

        legalPacmanActions = gameState.getLegalActions(0)

        for pacmanAction in legalPacmanActions:
            moveList.append(pacmanAction)
            scoreList.append(max_value( gameState.generateSuccessor(0, pacmanAction), 0, self.depth*gameState.getNumAgents()))

        optimalMove = moveList[index(max(scoreList))]

        return optimalMove

        util.raiseNotDefined()
        """

    def minimax(self, gameState, currentDepth, maxDepth):

        # call it with a new state basically
        # for every pacman action lets call the ghost actions one by one
        currentScoreList = []
        currentGhostScoreList = []

        pacmanScoreList = []
        pacmanMoveList = []

        #if(currentDepth==maxDepth):
        #    self.evaluationFunction(gameState)

        pacmanLegalActions = gameState.getLegalActions(0)
        #if(len(pacmanLegalActions)==1):
        #    pacmanScoreList = [0]
        #    pacmanMoveList = pacmanLegalActions[0]
        #    return pacmanScoreList, pacmanMoveList
        #else:
        for pacmanAction in pacmanLegalActions:
            newPacmanState = gameState.generateSuccessor(0, pacmanAction)
            for i in range(1, gameState.getNumAgents()):
                ghostLegalActions = newPacmanState.getLegalActions(i)
                for ghostAction in ghostLegalActions:
                    newGhostState = newPacmanState.generateSuccessor(i, ghostAction)
                    if(currentDepth==maxDepth):
                        currentGhostScoreList.append(self.evaluationFunction(gameState))
                    else:
                        currentGhostScoreList = self.minimax(newGhostState, currentDepth + 1, maxDepth)[0]
                if(currentGhostScoreList):
                    currentScoreList.append(min(currentGhostScoreList))
            pacmanScoreList.append(sum(currentScoreList))
            pacmanMoveList.append(pacmanAction)

        #bestAction = pacmanMoveList[pacmanScoreList.index(max(pacmanScoreList))]
        #return bestAction
        #print "stuff"
        #print "Pacman Score List: "+str(pacmanScoreList)
        #print "Pacman Move List: "+str(pacmanMoveList)

        return pacmanScoreList, pacmanMoveList

        util.raiseNotDefined()
    """
    def minimax(self, agentNumber, gameState, depth, player):

        winState = gameState.isWin()
        lostState = gameState.isLose()

        if winState:
            return self.evaluationFunction(gameState), 0

        elif lostState:
            return self.evaluationFunction(gameState), 0

        elif depth == self.depth:
            return self.evaluationFunction(gameState), 0

        # Set best and worst values according to agent
        # pacman maximizes and ghost minimizes
        if agentNumber == 0:
            best_value = -10000000000
        else:
            best_value = 10000000000

        legalMoves = gameState.getLegalActions(agentNumber)
        numberOfAgents = gameState.getNumAgents() - 1
        badMove = ''
        bestMove = ''

        # If it's a minimizing player, check if the agent is less than the num of agents, if so
        # continue at the same depth or else move depth+1 and find the worst move
        if not player:
            for i in range(len(legalMoves)):
                if agentNumber < numberOfAgents:
                    score, move = self.minimax(agentNumber + 1, gameState.generateSuccessor(agentNumber, legalMoves[i]), depth, False)
                else:
                    score, move = self.minimax(0, gameState.generateSuccessor(agentNumber, legalMoves[i]), depth + 1, True)
                if score < best_value:
                    bestMove, badMove = score, legalMoves[i]
            return bestMove, badMove
        # If it's a maximizing player, find the best move
        else:
            for i in range(len(legalMoves)):
                score, move = self.minimax(1, gameState.generateSuccessor(agentNumber, legalMoves[i]), depth, False)
                if score > best_value:
                    best_value, bestMove = score, legalMoves[i]
            return best_value, bestMove
    """
    """
        # if getLegalActions only has 1 member then return that anyways
        # only use evaluation function when the game is over
        pacmanScoreList, pacmanMoveList = self.minimax(gameState, 0, self.depth)

        bestAction = pacmanMoveList[pacmanScoreList.index(max(pacmanScoreList))]
        return bestAction
        util.raiseNotDefined()
        """
    """
        scoreList = []
        moveList = []

        legalPacmanActions = gameState.getLegalActions(0)

        for pacmanAction in legalPacmanActions:
            moveList.append(pacmanAction)
            scoreList.append(max_value( gameState.generateSuccessor(0, pacmanAction), 0, self.depth*gameState.getNumAgents()))

        optimalMove = moveList[index(max(scoreList))]

        return optimalMove

        util.raiseNotDefined()
        """
    """
    def minimax(self, gameState, currentDepth, maxDepth):

        # call it with a new state basically
        # for every pacman action lets call the ghost actions one by one
        currentScoreList = []
        currentGhostScoreList = []

        pacmanScoreList = []
        pacmanMoveList = []

        #if(currentDepth==maxDepth):
        #    self.evaluationFunction(gameState)

        pacmanLegalActions = gameState.getLegalActions(0)
        if(len(pacmanLegalActions)==1):
            pacmanScoreList = [0]
            pacmanMoveList = pacmanLegalActions[0]
            return pacmanScoreList, pacmanMoveList
        else:
            for pacmanAction in pacmanLegalActions:
                newPacmanState = gameState.generateSuccessor(0, pacmanAction)
                for i in range(1, gameState.getNumAgents()):
                    ghostLegalActions = newPacmanState.getLegalActions(i)
                    for ghostAction in ghostLegalActions:
                        newGhostState = newPacmanState.generateSuccessor(i, ghostAction)
                        if(currentDepth==maxDepth):
                            currentGhostScoreList.append(self.evaluationFunction(gameState))
                        else:
                            currentGhostScoreList = self.minimax(newGhostState, currentDepth + 1, maxDepth)[0]
                    if(currentGhostScoreList):
                        currentScoreList.append(min(currentGhostScoreList))
                pacmanScoreList.append(sum(currentScoreList))
                pacmanMoveList.append(pacmanAction)

        #bestAction = pacmanMoveList[pacmanScoreList.index(max(pacmanScoreList))]
        #return bestAction
        #print "stuff"
        #print "Pacman Score List: "+str(pacmanScoreList)
        #print "Pacman Move List: "+str(pacmanMoveList)

        return pacmanScoreList, pacmanMoveList

        util.raiseNotDefined()
    """
    """
    # takes a pacman state, returns the max score from all the ghost actions from the pacman state
    def max_value(self, newPacmanState, depth, maxDepth):
        maxScore = -float('inf')
        ++depth
        if(depth==maxDepth)
            return float(inf)
        for i in range(1, newPacmanState.getNumAgents()):
            ghostLegalActions = newPacmanState.getLegalActions(i)
            for ghostAction in ghostLegalActions:
                maxScore = max(maxScore, min_value(newPacmanState.generateSuccessor(i, ghostAction), depth, maxDepth))
                #if(maxScore<(min_value(newPacmanState.generateSuccessor(i, ghostAction))[0])
                #    maxScore = (min_value(newPacmanState.generateSuccessor(i, ghostAction))[0]
                #    optimalMove = ghostAction
        return maxScore
        util.raiseNotDefined()

    # takes a ghost state, returns minimum pacman score from all pacman actions from that ghost state
    def min_value(self, ghostState, depth, maxDepth):
        minScore = float('inf')
        pacmanLegalActions = ghostState.getLegalActions(0)
        for pacmanAction in pacmanLegalActions:
            minScore = min(minScore, max_value(ghostState.generateSuccessor(0, pacmanAction), depth, maxDepth))
            #if(minScore>=)
        return minScore
        util.raiseNotDefined()
    """

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction
          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """

        def maxAgent(state, depth):

            if state.isWin() or state.isLose():
                return state.getScore()

            # max agent is always pacman
            actions = state.getLegalActions(0)

            bestScore = float("-inf")
            score = bestScore
            bestAction = Directions.STOP

            goToDot = False

            #print "getfood length " + str(len(state.getFood().asList()))

            # the if-else makes the ghost not stop when it has only one dot remaining
            # remove the if else to make the ghost not rush towards the dot, but its gonna stop before the last dot in some cases

            # basic ghost bitch code
            if len(state.getFood().asList()) == 1 and depth == 0:
                from game import Actions
                actionVectors = [Actions.directionToVector( a, 1 ) for a in actions]
                pacmanPosition = state.getPacmanPosition()

                #newPositions = [( pacmanPosition[0]+a[0], pacmanPosition[1]+a[1] ) if a != Directions.STOP for a in actionVectors ]
                newPositions=[]
                for a in actionVectors:
                     if a != Directions.STOP and (pacmanPosition[0]+a[0], pacmanPosition[1]+a[1]) not in gameState.getWalls().asList():
                         newPositions.append((pacmanPosition[0]+a[0], pacmanPosition[1]+a[1]))

                # Select best actions given the state
                distancesToDot = [manhattanDistance( pos, state.getFood().asList()[0] ) for pos in newPositions]
                bestDotScore = min( distancesToDot )
                bestActions = [action for action, distance in zip( actions, distancesToDot ) if distance == bestDotScore]
                # set bestaction here
                if(len(bestActions)==1 and bestActions[0]==Directions.STOP):
                    print "into the if condiitons"
                    for action in actions:
                        score = minAgent(state.generateSuccessor(0, action), depth, 1)
                        if score > bestScore:
                            bestScore = score
                            bestAction = action
                else:
                    bestAction = bestActions[0]

                #print "bestactions: " +str(bestActions)
                #print "bestAction at one dot: " +str(bestAction)

            else:

                for action in actions:
                    score = minAgent(state.generateSuccessor(0, action), depth, 1)
                    if score > bestScore:
                        bestScore = score
                        bestAction = action

            if depth == 0:
                return bestAction
            else:
                return bestScore


        """
        def maxAgent(state, depth):

            if state.isWin() or state.isLose():
                return state.getScore()

            # max agent is always pacman
            actions = state.getLegalActions(0)

            bestScore = float("-inf")
            score = bestScore
            bestAction = Directions.STOP

            goToDot = False

            #print "getfood length " + str(len(state.getFood().asList()))

            # basic bitch code
            if len(state.getFood().asList()) == 1 and depth == 0:


                from game import Actions
                actionVectors = [Actions.directionToVector( a, 1 ) for a in actions]
                pacmanPosition = state.getPacmanPosition()

                #for i in range(1, state.getNumAgents()-1):
                #    if(manhattanDistance(pacmanPosition, state.getGhostPosition(i)) <= 5):
                #        goToDot=False

                newPositions = [( pacmanPosition[0]+a[0], pacmanPosition[1]+a[1] ) for a in actionVectors]

                # Select best actions given the state
                distanceToDot = [manhattanDistance( pos, state.getFood().asList()[0] ) for pos in newPositions]
                bestDotScore = min( distanceToDot )

                if(bestDotScore>1):
                    goToDot=False
                else:
                    bestActions = [action for action, distance in zip( actions, distanceToDot ) if distance == bestDotScore]

                    # set bestaction here
                    bestAction = bestActions[0]

                    print "getfood length " + str(state.getFood().asList())

                    goToDot=True

            if goToDot==False:
                #if (depth==0 and len(state.getFood().asList()) > 1) or (depth==1 and len(state.getFood().asList())>0):
                for action in actions:
                    score = minAgent(state.generateSuccessor(0, action), depth, 1)
                    if score > bestScore:
                        bestScore = score
                        bestAction = action



            if depth == 0:
                return bestAction
            else:
                return bestScore
        """


        def minAgent(state, depth, currentGhost):

            if state.isLose():
                return state.getScore()

            nextAgentNumber = currentGhost + 1
            if currentGhost == state.getNumAgents() - 1:
                nextAgentNumber = 0

            actions = state.getLegalActions(currentGhost)
            bestScore = float("inf")
            score = bestScore

            for action in actions:
                prob = 1.0/len(actions)
                # last ghost so its gonna be pacman's turn next
                if nextAgentNumber == 0:
                    if depth == self.depth - 1:
                        score = self.evaluationFunction(state.generateSuccessor(currentGhost, action))
                        score += prob * score
                    else:
                        score = maxAgent(state.generateSuccessor(currentGhost, action), depth + 1)
                        score += prob * score
                else:
                    score = minAgent(state.generateSuccessor(currentGhost, action), depth, nextAgentNumber)
                    score += prob * score

            return score

        return maxAgent(gameState, 0)





        """
        def expectimax(self, gameState, currentDepth, maxDepth):

            # call it with a new state basically
            # for every pacman action lets call the ghost actions one by one
            currentScoreList = []
            currentGhostScoreList = []

            pacmanScoreList = []
            pacmanMoveList = []

            #if(currentDepth==maxDepth):
            #    self.evaluationFunction(gameState)

            pacmanLegalActions = gameState.getLegalActions(0)
            #if(len(pacmanLegalActions)==1):
            #    pacmanScoreList = [0]
            #    pacmanMoveList = pacmanLegalActions[0]
            #    return pacmanScoreList, pacmanMoveList
            #else:
            for pacmanAction in pacmanLegalActions:
                newPacmanState = gameState.generateSuccessor(0, pacmanAction)
                for i in range(1, gameState.getNumAgents()):
                    ghostLegalActions = newPacmanState.getLegalActions(i)
                    prob = 1.0/ghostLegalActions
                    for ghostAction in ghostLegalActions:
                        newGhostState = newPacmanState.generateSuccessor(i, ghostAction)
                        if(currentDepth==maxDepth):
                            currentGhostScoreList.append(self.evaluationFunction(gameState)*prob)
                        else:
                            currentGhostScoreList = self.expectimax(newGhostState, currentDepth + 1, maxDepth)[0]
                    if(currentGhostScoreList):
                        currentScoreList.append(min(currentGhostScoreList)*prob)
                pacmanScoreList.append(sum(currentScoreList))
                pacmanMoveList.append(pacmanAction)

            #bestAction = pacmanMoveList[pacmanScoreList.index(max(pacmanScoreList))]
            #return bestAction
            #print "stuff"
            #print "Pacman Score List: "+str(pacmanScoreList)
            #print "Pacman Move List: "+str(pacmanMoveList)

            return pacmanScoreList, pacmanMoveList
        """

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    
    def closestDot(pos, foodPos):
        foodDistance = []
        for food in foodPos:
            foodDistance.append(util.manhattanDistance(food, pos))

        if len(foodDistance) > 0:
            return min(foodDistance)
        else:
            return 1

    def closestGhost(pos, ghosts):
        ghostDistance = []
        closestGhost = 0
        for ghost in ghosts:
            ghostDistance.append(util.manhattanDistance(ghost.getPosition(), pos))
            closestGhost=ghost

        if len(ghostDistance) > 0:
            return min(ghostDistance),closestGhost
        else:
            return 1,closestGhost

    def allFoodDots(pos, foodPositions):
        foodDistance = []
        for food in foodPositions:
            foodDistance.append(util.manhattanDistance(food, pos))
        return sum(foodDistance)

    def allGhosts(pos, ghosts):
        ghostDistance = []
        for ghost in ghosts:
            ghostDistance.append(util.manhattanDistance(ghost.getPosition(), pos))
        return sum(ghostDistance)

    def nearAGhost(pos, ghosts):
        near = False
        for ghost in ghosts:
            if util.manhattanDistance(ghost.getPosition(), pos) <= 5:
                near=True
        return near

    def numFood(pos, food):
        return len(food)

    pacmanPos = currentGameState.getPacmanPosition()
    score = currentGameState.getScore()
    foodList = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()

    #print str(currentGameState.getFood().height)

    maxDistanceFromGhost = math.sqrt((currentGameState.getFood().height * currentGameState.getFood().height)+(currentGameState.getFood().width*currentGameState.getFood().width))

    #print str(maxDistanceFromGhost)


    #print "score before: " +str(score)
    # if dot is closer than ghost, increase the score
    #print "score before: " +str(score)
    if closestDot(pacmanPos, foodList) < closestGhost(pacmanPos, ghosts)[0] + 3:
        score = score * 5
    else:
        if len(foodList)>10:
            score -= 0.7*allFoodDots(pacmanPos, foodList)
        else:
            score += 0.5*closestDot(pacmanPos, foodList)

    if closestGhost(pacmanPos, ghosts)[0]<=4:
        if closestGhost(pacmanPos, ghosts)[1] != 0:
            if(not (closestGhost(pacmanPos, ghosts)[1].scaredTimer>1)):
                score -= (maxDistanceFromGhost - closestGhost(pacmanPos, ghosts)[0]) * 10
            else:
                score += (maxDistanceFromGhost - closestGhost(pacmanPos, ghosts)[0]) * 5

    if closestDot(pacmanPos, foodList)!=0:
        score += (maxDistanceFromGhost - closestDot(pacmanPos, foodList))



    #print "score after food: " +str(score)

    #if nearAGhost(pacmanPos,ghosts):

    #else:
    #    score = score / 2
    #print "score after ghost: " +str(score)

    # decrease the score based on how far the dots are
    if len(foodList)>5:
        score -= 0.7*allFoodDots(pacmanPos, foodList)
    #print str(score)
    else:
        score += 0.5*closestDot(pacmanPos, foodList)
    #score += allGhosts(pacmanPos, ghosts)
    return score

    #import random
    #return currentGameState.getScore() * random.randint(-500,500)

# Abbreviation
better = betterEvaluationFunction
