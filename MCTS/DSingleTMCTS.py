import random
import time
from typing import Callable

import numpy as np
from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove

from Helper.Logging import PrintLog
from MCTS.MCTSNode import MCTSNode, Backpropagate, Playout, SelectChild

# Determinized single Tree MCTS
class DSingleTMCTS:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove], eval_function : Callable, visit_threshold=5, seed_count=1000, seeds:list[int]=None):
        self.EvaluationFunction = eval_function
        self.PossibleMoves = possible_moves
        self.GameState = game_state
        self.VisitThreshold = visit_threshold

        self.Seeds = seeds if seeds is not None else []
        if len (self.Seeds) < seed_count: # fill in random seeds if not enough provided
            self.Seeds += [random.randint(0, 2 ** 30) for _ in range(seed_count - len(self.Seeds))]

        self.EarlyStopping = False
        self.ElapsedTimeMs = 0

    def CheckForEarlyStopping(self, start_time: float, given_time_ms: int, buffer_time: int = 250) -> bool:
        self.ElapsedTimeMs = (time.perf_counter() - start_time) * 1000
        self.EarlyStopping = given_time_ms - self.ElapsedTimeMs < buffer_time
        return self.EarlyStopping


    # =========================MCTS Main Function========================
    def MonteCarloSearch(self, max_iterations: int, given_time_ms: int) -> BasicMove:
        PrintLog("MCTS", f"Starting MCTS with {max_iterations} iterations and {given_time_ms} ms time limit", 2)
        start_time = time.perf_counter()

        root = MCTSNode(None, None)
        root.ExpandRoot(self.GameState, self.PossibleMoves)

        for i in range(max_iterations):
            if self.EarlyStopping or self.CheckForEarlyStopping(start_time, given_time_ms):
                PrintLog("MCTS",
                         f"Early stopping at iteration {i + 1}/{max_iterations}, elapsed time: {int(self.ElapsedTimeMs)}/{given_time_ms - 150} ms",
                         2)
                break

            # Selection
            selected_child_node = SelectChild(root.Children)
            used_seed = selected_child_node.GameStates.keys()
            unused_seed = [seed for seed in self.Seeds if seed not in used_seed]
            while selected_child_node is not None and (selected_child_node.IsExpanded() or selected_child_node.IsTerminal()):
                selected_child_node = SelectChild(selected_child_node.GenIncompleteChildren(len(self.Seeds)))
                if selected_child_node is None:
                    continue
                used_seed = selected_child_node.GameStates.keys()
                unused_seed = [seed for seed in self.Seeds if seed not in used_seed]
                if selected_child_node.NumberOfVisits > self.VisitThreshold * len(used_seed) and len(unused_seed) > 0:
                    break # this break when the node is never expanded before the threshold is reached and there are still unused seeds


            if selected_child_node is None:
                PrintLog("MCTS",
                         f"Tree fully explored, stopping at iteration {i + 1}/{max_iterations}, elapsed time: {int(self.ElapsedTimeMs)}/{given_time_ms - 150} ms",
                         2)
                break

            if self.CheckForEarlyStopping(start_time, given_time_ms):
               continue

            # Expansion
            seed = random.choice(unused_seed)  # pick one determinization randomly
            child = selected_child_node.ProgressiveExpand(seed)

            if self.CheckForEarlyStopping(start_time, given_time_ms):
               continue

            # Simulation and Backpropagation
            terminal_game_state = Playout(child, self.EvaluationFunction, seed)
            utilityValue = self.EvaluationFunction(terminal_game_state)
            Backpropagate(child, utilityValue)

        avg_utilities = [child.AverageUtility for child in root.Children]
        best_index = int(np.argmax(avg_utilities))
        return self.PossibleMoves[best_index]



