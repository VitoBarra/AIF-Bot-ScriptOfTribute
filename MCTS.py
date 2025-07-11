import random
import time

import numpy as np

from scripts_of_tribute.board import GameState # EndGameState is an attribute of GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove



class MonteCarloTreeSearchNode:
    def __init__(self, game_state: GameState = None, possible_moves=None, parent=None, parent_move=None):
        self.game_state: GameState = game_state # it can be obtained with apply_move from the parent game_state
        self.parent: MonteCarloTreeSearchNode = parent
        self.parent_move: BasicMove = parent_move
        self.possible_moves:list[BasicMove] = possible_moves if possible_moves is not None else []
        self.Children: list[MonteCarloTreeSearchNode] = []
        for move in self.possible_moves:
            # Create a child node for each possible move
            self.Children.append(MonteCarloTreeSearchNode(None,None,self, move))

        self.number_of_visits = 0 # N(n)
        self.max_val = 0 # U(n)
        self.average_value = 0.0 # Q(n), average value of the node


    ##=========================Node kind check========================
    def is_leaf(self):
        return len(self.Children) == 0


    def is_terminal(self) -> bool:
        """
        @brief Check whether this node is a terminal node in the Monte Carlo Search Tree.

        A node is considered terminal if the move that led to it is an END_TURN command.
        This is used in Monte Carlo Tree Search to determine whether simulation or expansion
        should proceed.

        @return bool: True if this node is terminal (i.e., parent move ends the turn), False otherwise.
        """
        return self.parent_move.command == MoveEnum.END_TURN

    ##===============================================================
    def expand_node(self) -> 'MonteCarloTreeSearchNode':
        if len(self.Children) > 0:
            return self

        self.game_state, self.possible_moves = self.parent.game_state.apply_move(self.parent_move)  # Apply the move to the game state
        for move in self.possible_moves:
            # Create a child node for each possible move
            self.Children.append(MonteCarloTreeSearchNode(None,None,self, move))
        return self


    @staticmethod
    def calculate_ucb1_value(node: 'MonteCarloTreeSearchNode') -> float:
        #The theoretical value of c is sqrt(2), but only if  exploitation_term is in ranger [0,1]
        #that is not the case here, so we can use any value for c
        c = np.sqrt(2)

        exploitation_term = node.average_value

        if node.number_of_visits == 0:
            exploration_term = float('inf')  # If the node has never been visited, we want to explore it
        else:
            exploration_term = np.sqrt(np.log(node.parent.number_of_visits) / node.number_of_visits)

        return exploitation_term + c * exploration_term


    def child_node_selection(self) -> 'MonteCarloTreeSearchNode':
        best_ucb1 = float('-inf')
        best_child_node:MonteCarloTreeSearchNode|None = None

        for child_node in self.Children:
            ucb1 = self.calculate_ucb1_value(child_node)
            if ucb1 > best_ucb1:
                best_ucb1 = ucb1
                best_child_node = child_node
        if best_child_node is None:
            raise ValueError("No child node found")

        return best_child_node


    def playout(self) -> 'MonteCarloTreeSearchNode':
        current_node: MonteCarloTreeSearchNode = self

        while not current_node.is_terminal():
            # randomly select semple the non-deterministic state space
            current_node.expand_node()
            current_node: MonteCarloTreeSearchNode = random.choice(current_node.Children)

        # Expand the terminal node to get the game state and possible moves
        current_node.expand_node()

        # this cleanup is needed correctly to generate the non-deterministic tree
        self.Children = []
        return current_node

    def backpropagate(self, val) -> None:
        self.number_of_visits += 1
        # Update the average value and max value
        self.average_value += (val - self.average_value) / self.number_of_visits
        # Update the max value
        self.max_val = val if val > self.max_val else self.max_val

        if self.parent:
            self.parent.backpropagate(val)  # Parent is not a leaf

class MonteCarloTreeSearch:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove],
                 given_time: int, eval_function, max_playout=-1, ):
        self.root = MonteCarloTreeSearchNode(game_state, possible_moves) # root has no parent
        self.evaluation_function = eval_function
        self.given_time_ms = given_time
        self.start_time = time.perf_counter()
        self.max_playout = max_playout

    def some_time_left(self) -> bool:
        delta = time.perf_counter() - self.start_time
        time_elapsed_ms = delta * 1000
        return self.given_time_ms - time_elapsed_ms >  150


    def MonteCarloSearch(self) -> BasicMove:
        current_node = self.root

        if len(current_node.Children) == 1:
            best_move = current_node.Children[0]
            best_move.expand_node()
            #print(f"Best move: {best_move.move.command} with max value {best_move.max_val} and was visites {best_move.number_of_visits} times, move children {len(current_node.Children)}")
            return best_move.parent_move

        playoutCount = 0
        while self.some_time_left()  and (self.max_playout < 0 or self.max_playout > playoutCount ):
            selected_child_node:MonteCarloTreeSearchNode = current_node.child_node_selection()
            if selected_child_node.is_leaf():
                playoutCount += 1
                terminal_node: MonteCarloTreeSearchNode = selected_child_node.playout()
                node_evaluation = self.evaluation_function(terminal_node.game_state)
                terminal_node.backpropagate(node_evaluation)
                current_node = self.root
            else:
                current_node = selected_child_node

        return self.select_best_move()

    def select_best_move(self) -> BasicMove:
        return max(self.root.Children, key=lambda c: (c.max_val, c.number_of_visits)).move


