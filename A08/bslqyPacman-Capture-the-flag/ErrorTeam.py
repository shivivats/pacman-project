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

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'HunterAgent', second = 'ProtectAgent'):
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

class HunterAgent(CaptureAgent):
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
    
    if self.index % 2 == 0:
            boundary = (gameState.data.layout.width - 2) / 2
    else:
            boundary = ((gameState.data.layout.width - 2) / 2) + 1
    self.boundary = []
    for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(boundary, i):
            self.boundary.append((boundary, i))
    '''
    Your initialization code goes here, if you need any.
    '''
  # returns distance to nearest target and the nearest target from an array by using maze distance
  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)

  # returns distance to furthest target and the furthest target from an array by using maze distance
  def getFurthestTarget(self, gameState, pos, targets):
    maxDisttoTarget, furthestTarget = max([(self.getMazeDistance(pos, target), target) for target in targets])
    return furthestTarget

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

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)
    
    position = gameState.getAgentState(self.index).getPosition()
    hunterActions = []
    currFoodList = self.getFood(gameState).asList()
    maxLoad = 3
    
    load = gameState.getAgentState(self.index).numCarrying
        
    distanceToClosestEnemy = 100
    #fleeDistance = 3
    
    for a in actions :
        successor = self.getSuccessor(gameState, a)
        successor_position = successor.getAgentPosition(self.index)
        for i in self.getOpponents(successor):
            opponentPos = successor.getAgentState(i).getPosition()
            if opponentPos is not None and not successor.getAgentState(i).isPacman:
                dist = self.getMazeDistance(successor_position, opponentPos)
                if dist < distanceToClosestEnemy:
                    distanceToClosestEnemy = dist  
                    #positionOfClosestEnemy = opponentPos
                    
    #print self.getOpponents
    """if distanceToClosestEnemy <= fleeDistance and load == maxLoad -1:
         maxDistanceToEnemy = 0
         for a in actions:
             successor = self.getSuccessor(gameState, a)
             successor_position = successor.getAgentPosition(self.index)
             dist = self.getMazeDistance(successor_position, positionOfClosestEnemy)
             if dist > maxDistanceToEnemy :
                 actionToTake = a
                 maxDistanceToEnemy = dist"""
                 
    if load < maxLoad:
            #Collect closest food
            for a in actions :
                successor = self.getSuccessor(gameState, a)
                successor_position = successor.getAgentPosition(self.index)
                for f in currFoodList:
                    dist = self.getMazeDistance(successor_position, f)
                    """if dist < distanceToTarget:
                        actionToTake = a
                        distanceToTarget = dist"""
                    #print "DIST", distanceToClosestEnemy
                    
                    for i in self.getOpponents(successor):
                        opponentPos = successor.getAgentState(i).getPosition()
                        if opponentPos is not None :
                            if not successor.getAgentState(i).isPacman:
                                distToEnem = self.getMazeDistance(successor_position, opponentPos)
                                if distToEnem < distanceToClosestEnemy:
                                    distanceToClosestEnemy = 1/distToEnem  
                            else:
                                 distToEnem = self.getMazeDistance(successor_position, opponentPos)
                                 if distToEnem < distanceToClosestEnemy:
                                    distanceToClosestEnemy = distToEnem
                    if distanceToClosestEnemy < dist:
                        randBorder_position = random.choice(self.boundary)
                        for a in actions :
                            successor = self.getSuccessor(gameState, a)
                            successor_position = successor.getAgentPosition(self.index)
                            distGoal = self.getMazeDistance(successor_position, randBorder_position)
                            hunterActions.append((a, 100 + distGoal)) 
                    hunterActions.append((a, dist + distanceToClosestEnemy))
    else:
            enterPoint = self.getNearestTarget(gameState, position, self.boundary)
            for a in actions :
                successor = self.getSuccessor(gameState, a)
                successor_position = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(successor_position, enterPoint[1])
                """if dist < distanceToTarget :
                    actionToTake = a
                    distanceToTarget = dist"""
                hunterActions.append((a, dist))   

            #bestAction =  self.getBestAction(gameState, enterPoint[1], actions)
            # print "BestAction", bestAction
            #actionToTake = bestAction[1]       
    prevVal = hunterActions[0][1]
    nextAction = hunterActions[0][0]
    
    for ha in hunterActions:
        if ha[1] < prevVal:
            prevVal = ha[1]
            nextAction = ha[0]
    return nextAction

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != util.nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor




class ProtectAgent(CaptureAgent):
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
    if self.index % 2 == 0:
            boundary = (gameState.data.layout.width - 2) / 2
    else:
            boundary = ((gameState.data.layout.width - 2) / 2) + 1
    self.boundary = []
    for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(boundary, i):
            self.boundary.append((boundary, i))
    '''
    Your initialization code goes here, if you need any.
    '''
  # returns distance to nearest target and the nearest target from an array by using maze distance
  def getNearestTarget(self, gameState, pos, targets):
    minDis, nearestTarget = min([(self.getMazeDistance(pos, target), target) for target in targets])
    return (minDis, nearestTarget)

  # returns distance to furthest target and the furthest target from an array by using maze distance
  def getFurthestTarget(self, gameState, pos, targets):
    maxDisttoTarget, furthestTarget = max([(self.getMazeDistance(pos, target), target) for target in targets])
    return furthestTarget

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
    
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != util.nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    actions.remove(Directions.STOP)
    position = gameState.getAgentState(self.index).getPosition()
    
    defenderActions = []
    
    numAttackers = 0
    for i in self.getOpponents(gameState):    
        if gameState.getAgentState(i).isPacman:
            numAttackers += 1
            
    if numAttackers > 0:
         for a in actions :
            successor = self.getSuccessor(gameState, a)
            successor_position = successor.getAgentPosition(self.index)
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
            for inv in invaders: #print invaders[0]
                   for a in actions :
                       successor = self.getSuccessor(gameState, a)
                       successor_position = successor.getAgentPosition(self.index)
                       defenderActions.append( (a, self.getMazeDistance(successor_position, inv.getPosition()) ))
    else:
        randBorder_position = random.choice(self.boundary)
        for a in actions :
            successor = self.getSuccessor(gameState, a)
            successor_position = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(successor_position, randBorder_position)
            defenderActions.append((a, dist)) 
       
    nextAction = Directions.STOP
    if len(defenderActions) > 0:
        prevVal = defenderActions[0][1]
        nextAction = defenderActions[0][0]
             
        for da in defenderActions:
            if da[1] < prevVal:
                prevVal = da[1]
                nextAction = da[0]
            
    return nextAction
