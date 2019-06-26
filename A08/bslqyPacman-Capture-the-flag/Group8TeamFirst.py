# Group8Team.py
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
               first = 'CampingAgent', second = 'AttackerAgent'):
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

class CampingAgent(CaptureAgent):
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
    self.depth = 3
    self.targetPos = None


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    currPos = gameState.getAgentState(self.index).getPosition()
    currPos = (int(currPos[0]),int(currPos[1]))
    positions = self.getNeighbouringDots(gameState)
    #print(str(currPos) + " " + str(self.targetPos))
    if self.targetPos is None or currPos == self.targetPos:
        #print("hi")
        if len(positions) is 2:
            self.targetPos = random.choice(positions[1])
    
    return self.getBestAction(gameState, self.targetPos, actions)[1]
    #return random.choice(actions)

  def getNeighbouringDots(self, gameState):
      best = [0,0,0]
      best[0] = 0;
      food = self.getFoodYouAreDefending(gameState).asList()
      for currFood in food:
          visitedNodes = [currFood]
          sol = self.searchSurroundings(currFood, gameState, 1, self.depth, visitedNodes)
          if sol >= best[0]:
              best = [sol]
              #self.campingGround = sol
              best[0] = sol
              best.append(visitedNodes)
              #best[1] = currFood[0]
              #best[2] = currFood[1]
      #print(best)
      return best
      
      
  def searchSurroundings(self, currFood, gameState, numOfFood, currDepth, visited):
      x = currFood[0]
      y = currFood[1]
      food = self.getFoodYouAreDefending(gameState)
      
      if(currDepth> 0):
          currDepth -=1
          
          #Look up
          y -=1
          if (y>=1):
              if(gameState.getWalls()[x][y] == False):
                  if(food[x][y] == True and not (x,y) in visited):
                      #print("up true")
                      numOfFood +=1
                      visited.append((x,y))
                  numOfFood = self.searchSurroundings((x,y), gameState, numOfFood, currDepth, visited)    
          #look right
          y +=1
          x +=1
          if (x<=gameState.data.layout.width):
              if(gameState.getWalls()[x][y] == False):
                  if(food[x][y] == True and not (x,y) in visited):
                      #print("right true")
                      numOfFood +=1
                      visited.append((x,y))
                  numOfFood =self.searchSurroundings( (x,y), gameState, numOfFood, currDepth, visited)
          #look down
          x -=1
          y +=1
          if (y<=gameState.data.layout.height):
              if(gameState.getWalls()[x][y] == False):
                  if(food[x][y] == True and not (x,y) in visited):
                      #print("down true")
                      numOfFood += 1
                      visited.append((x,y))
                  numOfFood = self.searchSurroundings( (x,y), gameState, numOfFood, currDepth, visited)
          #look left
          y -=1
          x -=1
          if (x>=1):
              if(gameState.getWalls()[x][y] == False):
                  if(food[x][y] == True and not (x,y) in visited):
                      #print("left true")
                      numOfFood +=1
                      visited.append((x,y))
                  numOfFood = self.searchSurroundings( (x,y), gameState, numOfFood, currDepth, visited)
      return numOfFood
            
   # returns best action by getting minimum distance from all actions
  def getBestAction(self, gameState, targetPos, actions):
      minDis, bestAction = min([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
      #print("best action", minDis, action)
      #print([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
      return (minDis, bestAction)

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
              
              
              
      
class AttackerAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.targetPos = None
    self.attacking = True

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    
    currPos = gameState.getAgentState(self.index).getPosition()
    currPos = (int(currPos[0]),int(currPos[1]))
    #print(str(currPos) + " " + str(self.targetPos))
    if self.targetPos is None or currPos == self.targetPos:
        if(self.attacking):
            self.targetPos = random.choice(self.getFood(gameState).asList())
            self.attacking = False
        else:
            boundary = 0
            if self.red:
                boundary = (gameState.data.layout.width - 2) / 2
            else:
                boundary = ((gameState.data.layout.width - 2) / 2) + 1
            walls = gameState.getWalls()
            best = 9999
            for i in range(1, gameState.data.layout.height):
                if not walls[boundary][i]:
                    dist = self.getMazeDistance(currPos, (boundary, i))
                    if dist < best:
                        self.targetPos = (boundary, i)
                        best = dist
            self.attacking = True
                
    
    return self.getBestAction(gameState, self.targetPos, actions)[1]

  # returns best action by getting minimum distance from all actions
  def getBestAction(self, gameState, targetPos, actions):
      minDis, bestAction = min([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
      #print("best action", minDis, action)
      #print([(self.getMazeDistance(self.getSuccessor(gameState, action), targetPos), action) for action in actions])
      return (minDis, bestAction)

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
      
        