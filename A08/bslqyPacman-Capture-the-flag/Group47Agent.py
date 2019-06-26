## IMPROVEMENTS

## DEFENDER NEEDS AN ESTIMATED ENEMY DISTANCE
## ATTACKER SHOULD NOT GO INTO ONEWAYS IF GHOST IS NEAR

import game
import random, time, util
from game import Directions
from util import nearestPoint
from captureAgents import CaptureAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,  first = 'Attacker', second = 'Defender'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class ReflexAgent(CaptureAgent):
    '''Funtions taken from the ReflexAgent'''
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
        
    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        max_value = max(values)
        best_actions = [a for a, v in zip(actions, values) if v == max_value]
        return random.choice(best_actions)


class Attacker(ReflexAgent):
    def registerInitialState(self, gameState):
        ReflexAgent.registerInitialState(self, gameState)
        self.last_reversed = 0        

    def _get_food_left(self, gameState):
        food_list = self.getFood(gameState).asList()
        return len(food_list)

    def _get_closest_food_distance(self, gameState):
        food_list = self.getFood(gameState).asList()
        if len(food_list) == 0: return 0
        position = gameState.getAgentState(self.index).getPosition()
        return min([self.getMazeDistance(position, food) for food in food_list])

    def _get_power_up_distance(self, gameState):
        position = gameState.getAgentState(self.index).getPosition()
        power_ups = self.getCapsules(gameState)
        power_up_dist = 0
        if len(power_ups) > 0:
            power_up_dist = min([self.getMazeDistance(position, power_up) for power_up in power_ups])
        return power_up_dist
    
    def _get_reverse_direction(self, gameState, action):
        reverse_dir = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        return 1 if action == reverse_dir else 0

    def _get_enemy_information(self, gameState, action):
        position = gameState.getAgentState(self.index).getPosition()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        dangerous_enemies = []
        enemy_distance = 0
        danger = 0

        for enemy in enemies:
            if enemy.getPosition() != None:
                if (not enemy.isPacman) and (enemy.scaredTimer == 0):
                    dangerous_enemies.append(enemy)
        if dangerous_enemies:
            enemy_distance = min([self.getMazeDistance(position, enemy.getPosition()) for enemy in dangerous_enemies])
            if enemy_distance <= 1:
                danger = 1

        return enemy_distance, danger
            
    def _get_distance_to_safety(self, gameState):
        border = []
        x = gameState.data.layout.width/2
        if self.red: x -= 1
        
        for y in range(gameState.data.layout.height):
            if not gameState.data.layout.walls[x][y]:
                border.append((x, y))

        position = gameState.getAgentState(self.index).getPosition()
        distance_to_safety = min([self.getMazeDistance(position, coords) for coords in border])
        return distance_to_safety

    # def _get_one_way(self, gameState):
    #     distance_to_enemy, _ = self._get_enemy_information(gameState, 'Stop')
    #     legal_actions = gameState.getLegalActions(self.index)

    #     if distance_to_enemy == 0:
    #         return legal_actions
        
    #     possible_actions = gameState.getLegalActions(self.index)
    #     if len(possible_actions) <= 2:
    #         return legal_actions
    #     #print('Searching for One Way')
    #     #print('Possible Actions:', possible_actions)
    #     enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    #     enemy_positions = [enemy.getPosition() for enemy in enemies]

    #     def check_one_way_recursively(gameState, distance_to_enemy, action):
    #         state = self.getSuccessor(gameState, action)

    #         possible_actions = state.getLegalActions(self.index)
    #         possible_actions.remove('Stop')
    #         # if Directions.REVERSE[action] in possible_actions:
    #         #     possible_actions.remove(Directions.REVERSE[action])
            
    #         # end of oneway
    #         if len(possible_actions) == 1:
    #             return 0

    #         # more than one possible way
    #         if len(possible_actions) >= 3:
    #             return 1

    #         # direction of enemy
    #         if state.getAgentPosition(self.index) == enemy.getPosition():
    #             return 0

    #         for a in possible_actions:
    #             return check_one_way_recursively(state, distance_to_enemy, a)
            
    #     save_actions = []
    #     for action in possible_actions:
    #         if check_one_way_recursively(gameState, distance_to_enemy, action) == 1:
    #             save_actions.append(action)

    #     #print('Save actions:', save_actions)

    #     if len(possible_actions)-1 > len(save_actions):
    #         print('Possible Actions:', possible_actions)
    #         print('Save actions:', save_actions)
    #         print('Well I guess something worked')

    #     return save_actions

    # def chooseAction(self, gameState):
    #     # actions = self._get_one_way(gameState)
    #     values = [self.evaluate(gameState, a) for a in actions]
    #     max_value = max(values)
    #     best_actions = [a for a, v in zip(actions, values) if v == max_value]
    #     return random.choice(best_actions)
        
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor_state = self.getSuccessor(gameState, action)
        features['food_left'] = self._get_food_left(successor_state)
        features['closest_food_distance'] = self._get_closest_food_distance(successor_state)
        features['power_up_distance'] = self._get_power_up_distance(successor_state)
        features['reverse'] = self._get_reverse_direction(gameState, action)
        features['stop'] = 1 if action == Directions.STOP else 0
        features['enemy_distance'], features['danger'] = self._get_enemy_information(successor_state, action)
        features['safety_distance'] = self._get_distance_to_safety(successor_state)

        #print features
        #print(Directions.REVERSE['West'])

        return features

    def getWeights(self, gameState, action):
        weights = util.Counter()
        weights['food_left'] = -100
        weights['closest_food_distance'] = -3
        weights['power_up_distance'] = -10
        weights['reverse'] = -50
        weights['stop'] = -200
        weights['enemy_distance'] = 1
        weights['danger'] = -100
        weights['safety_distance'] = 0

        # updates depending on situations
        successor_state = self.getSuccessor(gameState, action)
        position = successor_state.getAgentState(self.index).getPosition()
        carrying = gameState.getAgentState(self.index).numCarrying
        enemy_dist, danger = self._get_enemy_information(successor_state, action)
        if carrying > 0:
            if (enemy_dist > 0) and (enemy_dist < 8):
                weights['safety_distance'] = -5 * carrying
        if carrying > 10:
            weights['safety_distance'] = -100
        
        if danger == 1:
            weights['power_up_distance'] = -20
        if self._get_food_left(gameState) == 0:
            weights['safety_distance'] = -90

        return weights

class Defender(ReflexAgent):
    def registerInitialState(self, gameState):
        ReflexAgent.registerInitialState(self, gameState)
        self.last_food_list = self.getFoodYouAreDefending(gameState).asList()
        self.partolline = 19
        if self.red:
            self.partolline = 12

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0

        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)
        features['danger'] = 0
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
            if (min(dists) < 2) and (successor.getAgentState(self.index).scaredTimer > 0):
                features['danger'] = 1
        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        # New Features if default map
        # if myPos[0] != self.partolline:
        #     features['distance_to_partol'] = self.getMazeDistance(myPos, (self.partolline, 8))
        # else:
        #     features['distance_to_partol'] = abs(self.partolline-myPos[0])
        # # print features
        # print myPos
        #features['distance_to_partol'] = 0
        return features

    def getWeights(self, gameState, action):
        #return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'distance_to_partol': -5}
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'distance_to_partol': -2, 'danger': -1000}

