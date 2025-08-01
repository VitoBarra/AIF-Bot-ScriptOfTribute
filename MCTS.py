import random
import time
import copy
from typing import Callable

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


    def playout_policy_greedy_heuristic(self, eval_function:Callable) -> 'MonteCarloTreeSearchNode':
        for node in self.Children:
            node.expand_node()
        move_value = {node: eval_function(node.game_state) for node in self.Children}
        for node in self.Children:
            node.Children = []  # Clear the children to avoid memory leaks
            node.possible_moves = []
        return max(move_value, key=move_value.get)

    def playout_policy_greedy_heuristic_lookAhead(self, eval_function:Callable) -> 'MonteCarloTreeSearchNode':
        move_value = {}
        for node in self.Children:
            node.expand_node()
            move_value[node] = eval_function(node.game_state)  # Evaluate the game state of the node valued as the baseline of the move
            for child in node.Children:
                child.expand_node()
                val = eval_function(child.game_state)
                if node not in move_value or val > move_value[node]:
                    move_value[node] = val # Update the move value if the child has a better value to guide the search

        return max(move_value, key=move_value.get)



    def playout_policy_random(self) -> 'MonteCarloTreeSearchNode':
        return random.choice(self.Children)

    def deterministic_test(self):
        pgs = self.parent.game_state
        sgs1, ps1 = pgs.apply_move(self.parent_move)
        sgs1.initial_seed = 48

        for pick in ps1:
            sgs2, ps2 = sgs1.apply_move(pick)
            sgs21, ps21 = sgs1.apply_move(pick)
            for tavern_card2 in sgs2.tavern_available_cards:
                for tavern_card21 in sgs21.tavern_available_cards:
                    if tavern_card2.name != tavern_card21.name:
                        pass
            if len(ps2) != len(ps21):
                pass

    def playout(self, eval_function, depthMap) -> 'MonteCarloTreeSearchNode':
        current_node: MonteCarloTreeSearchNode = self

        # self.deterministic_test()

        depth = 0
        while not current_node.is_terminal():
            # randomly select semple the non-deterministic state space
            current_node.expand_node()
            # current_node: MonteCarloTreeSearchNode = current_node.playout_policy_random()
            # current_node: MonteCarloTreeSearchNode = current_node.playout_policy_greedy_heuristic(eval_function)
            current_node: MonteCarloTreeSearchNode = current_node.playout_policy_greedy_heuristic_lookAhead(eval_function)

            depth += 1
        depthMap[depth] = depthMap.get(depth, 0) + 1

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
    early_stopping_time = 0

    def __init__(self, game_state: GameState, possible_moves: list[BasicMove],
                 given_time: int, eval_function, max_playout=-1):
        self.depthMap = {}
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
                terminal_node: MonteCarloTreeSearchNode = selected_child_node.playout(self.evaluation_function,self.depthMap)
                node_evaluation = self.evaluation_function(terminal_node.game_state)
                terminal_node.backpropagate(node_evaluation)
                current_node = self.root
            else:
                current_node = selected_child_node

        self.print_monte_carlo_statistics()
        return self.select_best_move()

    def select_best_move(self) -> BasicMove:
        best_move = max(self.root.Children, key=lambda c: (c.max_val, c.number_of_visits))
        print (f"Best move: {best_move.parent_move.command} with max value {best_move.max_val} was visites {best_move.number_of_visits} times, move children {len(self.root.Children)};")
        if best_move.parent_move.command == MoveEnum.END_TURN and len(self.root.Children) > 1:
            MonteCarloTreeSearch.early_stopping_time += 1
            print (f"Early stopping time: {MonteCarloTreeSearch.early_stopping_time} times, move ignored {len(self.root.Children)}. End Turn with score {best_move.max_val} and visits {best_move.number_of_visits} times")
            for child in self.root.Children:
                if child.parent_move.command != MoveEnum.END_TURN:
                    print(f"    ignored move: {child.parent_move.command} with max value {child.max_val} was visites {child.number_of_visits} times")

        return best_move.parent_move





    def print_monte_carlo_statistics(self) -> None:
        visit_list = [child.number_of_visits for child in self.root.Children]
        total_visit = sum(visit_list)
        total_depth_visits = sum(self.depthMap.values())
        if total_visit != total_depth_visits :
            print(f"[Warning]: total visit count {total_visit} does not match total depth visits {total_depth_visits}")

        depth_summary = {
            depth: f"{count} ({(count / total_depth_visits) * 100:.2f}%)"
            for depth, count in sorted(self.depthMap.items())
        }
        print("Monte Carlo Tree Search statistics:")
        print(f"   time left: {self.given_time_ms - ((time.perf_counter() - self.start_time) * 1000):.4f} ms, playout executed {total_visit}")
        print(f"   visit distribution: {visit_list}")
        print(f"   depth distribution: {depth_summary}")

