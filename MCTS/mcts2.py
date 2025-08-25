from __future__ import annotations

import time

from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove
from scripts_of_tribute.enums import MoveEnum
from BotCommon.CommonCheck import obtain_move_semantic_id
from Helper.Logging import PrintLog
from MCTS.Common import calculate_ucb, playout
import random


class Node:
    def __init__(self):
        self.children: dict[tuple, NotRootNode] = {}
        # for ucb calculations
        self.number_of_playouts = 0
        self.total_utility = 0

    def expand(self, move: BasicMove, semantic_id: tuple):
        child = NotRootNode(self, move)
        if semantic_id in self.children.keys():
            raise ValueError(f"Child with semantic_id {semantic_id} already exists.")
        self.children[semantic_id] = child

    def search_unexpanded_child(self, possible_moves: list[BasicMove]) -> NotRootNode | None:
        for move in possible_moves:
            semantic_id = obtain_move_semantic_id(move)
            if semantic_id not in self.children:
                self.expand(move, semantic_id)
                return self.children[semantic_id]
        return None

class NotRootNode(Node):
    def __init__(self, parent, parent_move):
        super().__init__()
        self.parent: Node = parent
        self.parent_move: BasicMove = parent_move

    def calculate_ucb(self):
        return calculate_ucb(self.total_utility, self.number_of_playouts, self.parent.number_of_playouts)

    def back_propagation(self, utility):
        current_node = self
        while current_node is not None:
            current_node.number_of_playouts += 1
            current_node.total_utility += utility

            if hasattr(current_node, 'parent'):
                current_node = current_node.parent
            else:
                current_node = None

    def update_parent_move(self, moves: list[BasicMove]):
        parent_move_semantic_id = obtain_move_semantic_id(self.parent_move)
        for move in moves:
            semantic_id = obtain_move_semantic_id(move)
            if semantic_id == parent_move_semantic_id:
                self.parent_move = move
                return

        raise ValueError("parent move not found")

class RootNode(Node):
    def __init__(self, game_state, possible_moves):
        super().__init__()
        self.game_state: GameState = game_state
        self.possible_moves: list[BasicMove] = possible_moves

class MCTS2:
    def __init__(self, game_state, possible_moves, player_id, evaluation_function, seed = None):
        self.root = RootNode(game_state, possible_moves)
        self.player_id = player_id
        self.evaluation_function = evaluation_function
        self.seed = seed
        random.seed(16)

    def evaluation(self, game_state: GameState) -> float:
        return self.evaluation_function(game_state)

    def playout_and_back_prop(self, node, game_state):
        terminal_game_state = playout(node.parent_move, game_state, self.player_id)
        utility = self.evaluation(terminal_game_state)
        node.back_propagation(utility)

    def iteration(self):
        actual_node = self.root
        actual_game_state = self.root.game_state
        actual_possible_moves = self.root.possible_moves

        new_child = None
        while new_child is None:
            if actual_game_state.current_player.player_id != self.player_id:
                raise ValueError("Searching too deep")

            new_child: NotRootNode | None = actual_node.search_unexpanded_child(actual_possible_moves)

            if new_child is None:
                actual_node = MCTS2.selection(actual_node.children, actual_possible_moves)

                actual_node.update_parent_move(actual_possible_moves)

                if actual_node.parent_move.command == MoveEnum.END_TURN:
                    self.playout_and_back_prop(actual_node, actual_game_state)
                    break

                try:
                    actual_game_state, actual_possible_moves = actual_game_state.apply_move(actual_node.parent_move, self.seed)
                except Exception as e:
                    print(e)
                    raise ValueError (f"problems with apply_move, Move: {actual_node.parent_move} ")

            elif new_child is not None:
                self.playout_and_back_prop(new_child, actual_game_state)

    @staticmethod
    def selection (nodes: dict[tuple, NotRootNode], possible_moves: list[BasicMove]) -> NotRootNode:
        actual_children: list[NotRootNode] = []
        for possible_move in possible_moves:
            semantic_id = obtain_move_semantic_id(possible_move)
            if semantic_id in nodes.keys():
                actual_child = nodes[semantic_id]
                actual_children.append(actual_child)

        if len(actual_children) == 0:
            print(len(actual_children))
            print(len(nodes))
            print(len(possible_moves))
            raise ValueError("no actual child found")

        best_node = actual_children[0]
        best_ucb = float('-inf')

        for node in actual_children:
            ucb = node.calculate_ucb()
            if ucb > best_ucb:
                best_node = node
                best_ucb = ucb

        return best_node

    def MonteCarloSearch(self, max_iterations:int, given_time:int) -> BasicMove:
        PrintLog(f"MCTS", f"start move choice with {len(self.root.possible_moves)} possible moves and {max_iterations} iterations with {given_time} ms time limit",1)
        start_time = time.perf_counter()
        for i in range(max_iterations):
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000
            if given_time - elapsed_time_ms < 50:
                PrintLog("MCTS",
                         f"Early stopping at iteration {i + 1}/{max_iterations}, elapsed time: {int(elapsed_time_ms)}/{given_time} ms",
                         2)
                break
            self.iteration()

        best_move = random.choice(self.root.possible_moves)
        best_utility = float('-inf')

        if len(self.root.children.values()) != len(self.root.possible_moves):
            PrintLog(f"MCTS", f"didn't have time to check all the move, given time: {given_time}",1)

        nodes = self.root.children.values()
        for node in nodes:
            if node.total_utility > best_utility:
                best_utility = node.total_utility
                best_move = node.parent_move

        return best_move