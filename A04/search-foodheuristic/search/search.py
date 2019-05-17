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

    #util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
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
    priority_queue.push((start_node, action, cost), cost)

    print "DONT WORRY THE PROGRAM HASNT STOPPED"

    # Keep going until the priority_queue is empty
    while not priority_queue.isEmpty():
        top = priority_queue.pop()
        # If goal state is reached, return the list of actions
        if problem.isGoalState(top[0]):
            return top[1]

        # If the goal state is not reached, push all the successors which have not been
        #  visited yet to the priority_queue.
        if top[0] not in visited_state:
            visited_state[top[0]] = True
            for succ, act, co in problem.getSuccessors(top[0]):
                if succ and succ not in visited_state:
                    # Add the heuristic value in the priority cost.
                    priority_queue.push((succ, top[1] + [act], top[2] + co), top[2] + co + heuristic(succ, problem))

    #util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
