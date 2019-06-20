# search.py
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    from util import Stack
    # stack is the "Stack" which stores the node of the form (start_node, action, cost)
    stack = Stack()
    # visited_state keeps the track of nodes while visiting the grid.
    visited_state = {}
    # start_node is the current Pac Man position
    start_node = problem.getStartState()
    # cost is the total cost up till the current position.
    cost = 0
    # action is the list of all the actions required to reach from the initial pacman position
    # to the start_node position.
    action = []
    stack.push((start_node, action, cost))

    # Keep going until the stack is empty
    while not stack.isEmpty():
        top = stack.pop()
        # If goal state is reached, return the list of actions
        if problem.isGoalState(top[0]):
            return top[1]

        # If the goal state is not reached, push all the successors which has not been visited yet to the stack.
        if top[0] not in visited_state:
            visited_state[top[0]] = True
            for succ, act, co in problem.getSuccessors(top[0]):
                if succ and succ not in visited_state:
                    stack.push((succ, top[1] + [act], top[2] + co))

    util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    from util import Queue
    # queue is the "Queue" which stores the node of the form (start_node, action, cost)
    queue = Queue()
    # visited_state keeps the track of nodes while visiting the grid.
    visited_state = {}
    # start_node is the current Pac Man position
    start_node = problem.getStartState()
    # cost is the total cost up till the current position.
    cost = 0
    # action is the list of all the actions required to reach from the initial pacman position
    #  to the start_node position.
    action = []
    queue.push((start_node, action, cost))

    # Keep going until the queue is empty
    while not queue.isEmpty():
        top = queue.pop()
        # If goal state is reached, return the list of actions
        if problem.isGoalState(top[0]):
            return top[1]

        # If the goal state is not reached, push all the successors which has not been visited yet to the queue.
        if top[0] not in visited_state:
            visited_state[top[0]] = True
            for succ, act, co in problem.getSuccessors(top[0]):
                if succ and succ not in visited_state:
                    queue.push((succ, top[1] + [act], top[2] + co))

    util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue
    # priority_queue is the "PriorityQueue" which stores the node of the form ((start_node, action, cost), priority))
    priority_queue = PriorityQueue()
    # visited_state keeps the track of nodes while visiting the grid.
    visited_state = {}
    # start_node is the current Pac Man position
    start_node = problem.getStartState()
    # cost is the total cost up till the current position.
    cost = 0
    # action is the list of all the actions required to reach from the initial pacman position
    # to the start_node position.
    action = []
    # priority in this case will be equal to the cost.
    priority_queue.push((start_node, action, cost), cost)

    # Keep going until the priority_queue is empty
    while not priority_queue.isEmpty():
        top = priority_queue.pop()
        # If goal state is reached, return the list of actions
        if problem.isGoalState(top[0]):
            return top[1]

        # If the goal state is not reached, push all the successors which have
        # not been visited yet to the priority_queue.
        if top[0] not in visited_state:
            visited_state[top[0]] = True
            for succ, act, co in problem.getSuccessors(top[0]):
                if succ and succ not in visited_state:
                    priority_queue.push((succ, top[1] + [act], top[2] + co), top[2] + co)

    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

"""
def aStarSearch(problem, heuristic=nullHeuristic):
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue
    import Queue
    import threading
    import time

    exitFlag = 0

    class myThread (threading.Thread):
       def __init__(self, threadID, name, q):
          threading.Thread.__init__(self)
          self.threadID = threadID
          self.name = name
          self.q = q
       def run(self):
          print "\nStarting " + self.name
          while not exitFlag:
              # Keep going until the priority_queue is empty
                while not priority_queue.isEmpty():
                    top = priority_queue.pop()
                    # If goal state is reached, return the list of actions
                    if problem.isGoalState(top[0]):
                        returnThing(top[1])

                    # If the goal state is not reached, push all the successors which have not been
                    #  visited yet to the priority_queue.
                    if top[0] not in visited_state:
                        visited_state[top[0]] = True
                        for succ, act, co in problem.getSuccessors(top[0]):
                            if succ and succ not in visited_state:
                                # Add the heuristic value in the priority cost.
                                priority_queue.push((succ, top[1] + [act], top[2] + co), top[2] + co + heuristic(succ, problem))
          print "\nExiting " + self.name



    threadList = ["Thread-1", "Thread-2", "Thread-3"]
    queueLock = threading.Lock()
    threads = []
    threadID = 1

    # priority_queue is the "PriorityQueue" which stores the node of the form ((start_node, action, cost), priority))
    priority_queue = PriorityQueue()
    # visited_state keeps the track of nodes while visiting the grid.
    visited_state = {}
    # start_node is the current Pac Man position
    start_node = problem.getStartState()
    # cost is the total cost up till the current position.
    cost = 0
    # action is the list of all the actions required to reach from the initial pacman position
    # to the start_node position.
    action = []

    returnThing = []

    # Fill the queue
    #for word in nameList:
    #   priority_queue.put(word)
    # here is where we put data into the queue
    priority_queue.push((start_node, action, cost), cost)

    # Wait for queue to empty
    #while not priority_queue.empty():
    #   pass
    # Keep going until the priority_queue is empty
          thread = myThread(threadID, "new thread"+str(threadID))
              thread.start()
              threads.append(thread)
              threadID += 1


            #for t in threads:
            #   t.join()

        #for t in threads:
        #   t.join()

        # If goal state is reached, return the list of actions
        #if problem.isGoalState(top[0]):
            #return top[1]

        # If the goal state is not reached, push all the successors which have not been
        #  visited yet to the priority_queue.
        #if top[0] not in visited_state:
            #visited_state[top[0]] = True
            #for succ, act, co in problem.getSuccessors(top[0]):
                #if succ and succ not in visited_state:
                    # Add the heuristic value in the priority cost.
                    #priority_queue.push((succ, top[1] + [act], top[2] + co), top[2] + co + heuristic(succ, problem))

    # Notify threads it's time to exit
    exitFlag = 1

    # Wait for all threads to complete
    for t in threads:
       t.join()
    print "Exiting Main Thread"

    util.raiseNotDefined()
"""


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    # https://en.wikipedia.org/wiki/A*_search_algorithm
    # command: python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic


    """

    This assignment was solved together with groups Error 404 and Group 8, hence why we have the same solution.

    """


    from util import PriorityQueue
    from game import Directions

    priority_queue = PriorityQueue()
    # visited_state keeps the track of nodes while visiting the grid.
    visited_state = {}
    # start_node is the current Pac Man position
    start_node = problem.getStartState()
    # cost is the total cost up till the current position.
    cost = 0
    # action is the list of all the actions required to reach from the initial pacman position
    # to the start_node position.
    action = []
    priority_queue.push((start_node, action, cost), cost)

    threadList = []
    index = 0
    solution = []
    # Keep going until the priority_queue is empty
    while not solution and (len(threadList) > 0 or index == 0):
        if not priority_queue.isEmpty():
            top = priority_queue.pop()

            #print "T", len(top[1])
            if problem.isGoalState(top[0]):
                solution = top[1]
            else:
                t = myThread(index, problem, top, priority_queue, visited_state, threadList, heuristic)
                threadList.append(t);
                t.start()
                index = index + 1
    #print "Solution", solution
    #print "threadList", len(threadList)
    return solution

import threading

class myThread (threading.Thread):
   def __init__(self, index, problem, top, priority_queue, visited_state, threadList, heuristic=nullHeuristic):
      threading.Thread.__init__(self)
      self.problem = problem
      self.top = top
      self.visited_state = visited_state
      self.heuristic = heuristic
      self.threadList = threadList
      self.index = index
      self.priority_queue = priority_queue
   def run(self):
      aStarUtil(self, self.problem, self.top, self.priority_queue, self.visited_state, self.threadList, self.heuristic)

def aStarUtil(thread, problem, top, priority_queue, visited_state, threadList, heuristic):
            # If goal state is reached, return the list of actions
            # If the goal state is not reached, push all the successors which have not been
            #  visited yet to the priority_queue.
            if top[0] not in visited_state:
                visited_state[top[0]] = True
                for succ, act, co in problem.getSuccessors(top[0]):
                    if succ and succ not in visited_state:
                        # Add the heuristic value in the priority cost.
                        priority_queue.push((succ, top[1] + [act], top[2] + co), top[2] + co + heuristic(succ, problem))
            #threadList.remove(thread)



# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
