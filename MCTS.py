import numpy as np

from scripts_of_tribute.board import GameState # EndGameState is an attribute of GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.Heuristics import utilityFunction_MIXMAXAVERAGERES

import time

class MonteCarloTreeSearchNode:
    def __init__(self, game_state: GameState, untried_moves=None, parent=None, parent_move=None):
        self.game_state: GameState = game_state # it can be obtained with apply_move from the parent game_state
        self.parent: MonteCarloTreeSearchNode = parent
        self.parent_move: BasicMove = parent_move
        if untried_moves is None:
            self.untried_moves: list[BasicMove] = []
        self.children: list[MonteCarloTreeSearchNode] = []
        self.number_of_visits = 0 # N(n)
        self.max_val = 0 # U(n)
        self.is_leaf = True

    @staticmethod
    def my_ucb1(node):
        c = np.sqrt(2)  # In theory should be np.sqrt(2), but we can test other parameters

        exploitation_term = node.max_val / node.number_of_visits
        exploration_term = np.sqrt(np.log(node.number_of_visits) / node.number_of_visits)

        return exploitation_term + c * exploration_term

    def child_node_selection(self, selection_function):
        # Nodes not expanded yet come first
        if len(self.untried_moves) > 0:
            return self.node_expansion(self.untried_moves[0])

        best_ucb1 = 0
        best_child_node = None  # should be MonteCarloTreeSearchNode

        for child_node in self.children:
            ucb1 = selection_function(child_node)
            if ucb1 > best_ucb1:
                best_ucb1 = ucb1
                best_child_node = child_node

        if best_child_node is None:
            raise ValueError("No child node found")

        return best_child_node

    def node_expansion(self, untried_move: BasicMove):
        # Remove untried_move from self.untried_moves
        # Be careful: DO NOT REMOVE UNTRIED_MOVE FROM THE LIST BEFORE CALLING THIS METHOD
        if untried_move in self.untried_moves:
            self.untried_moves.remove(untried_move)
        else :
            raise ValueError("The move is not in the untried moves list")

        # Create the child node
        child_game_state, child_moves = self.game_state.apply_move(untried_move)
        child_node = MonteCarloTreeSearchNode(child_game_state, child_moves, self, untried_move)

        # Add child_node to the children list
        self.children.append(child_node)
        return child_node

    def is_terminal(self) -> bool:
        return self.parent_move.command == MoveEnum.END_TURN
            
    # def playout_recursive(self, heuristic): # Must return a MonteCarloTreeSearchNode
    #
    #     if self.is_terminal():
    #         return self
    #
    #     best_move_val = -1
    #     best_move = None
    #
    #     for untried_move in self.untried_moves:
    #         child_game_state, _ = self.game_state.apply_move(untried_move)
    #         val = heuristic(child_game_state)
    #         if val > best_move_val:
    #             best_move_val = val
    #             best_move = untried_move
    #
    #     best_child: MonteCarloTreeSearchNode = self.node_expansion(best_move)
    #
    #     return best_child.playout_recursive(heuristic)

    def playout(self, heuristic):
        current_node: MonteCarloTreeSearchNode = self

        while not current_node.is_terminal():

            best_move_val = -1
            best_move = None

            for untried_move in current_node.untried_moves:
                child_game_state, _ = current_node.game_state.apply_move(untried_move)
                val = heuristic(child_game_state)
                if val > best_move_val:
                    best_move_val = val
                    best_move = untried_move

            best_child: MonteCarloTreeSearchNode = current_node.node_expansion(best_move)
            current_node = best_child

        return current_node
    
    def evaluate_terminal_node (self, heuristic):
        return heuristic(self.game_state)

    def backpropagate(self, val, is_leaf = True):
        self.number_of_visits += 1
        self.is_leaf = is_leaf
        if val > self.max_val:
            self.max_val = val # The paper says that for Tales of tribute using the max instead of the sum is better
        if self.parent:
            self.parent.backpropagate(val, False) # Parent is not a leaf

class MonteCarloTreeSearch:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove], given_time: int):
        self.root = MonteCarloTreeSearchNode(game_state, possible_moves) # root has no parent
        self.heuristic = utilityFunction_MIXMAXAVERAGERES
        self.given_time = given_time # Given time in seconds
        self.start_time = time.time() # Seconds elapsed from Epoch

    def some_time_left(self) -> bool:
        time_elapsed = time.time() - self.start_time
        return time_elapsed < self.given_time

    def tree_building(self):

        current_node = self.root

        while self.some_time_left():
            selected_child_node = current_node.child_node_selection(MonteCarloTreeSearchNode.my_ucb1)
            if selected_child_node.is_leaf:
                terminal_node: MonteCarloTreeSearchNode = selected_child_node.playout()
                val = terminal_node.evaluate_terminal_node(self.heuristic)
                terminal_node.backpropagate(val)
                current_node = self.root
            elif not selected_child_node.is_leaf:
                current_node = selected_child_node

        self.move_choice()

    def move_choice(self):

        max_val = -1
        move = None

        for child in self.root.children:
            if child.max_val > max_val:
                max_val = child.max_val
                move = child.parent_move
                
        return move