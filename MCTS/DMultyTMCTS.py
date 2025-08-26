import random
import time
from typing import Callable

import numpy as np
from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove

from Helper.Logging import PrintLog
from MCTS.MCTSNode import MCTSNode, Backpropagate, Playout, SelectChild

# Determinized multy Tree MCTS
class DMultyTCTS:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove], eval_function : Callable, tree_count:int= 5, tree_seeds:list[int]=None):
        self.EvaluationFunction = eval_function
        self.PossibleMoves = possible_moves
        self.GameState = game_state

        self.TreeCount = tree_count
        self.TreeSeeds = tree_seeds if tree_seeds is not None else []
        if len (self.TreeSeeds) < tree_count: # fill in random seeds if not enough provided
            self.TreeSeeds += [random.randint(0, 2**30) for _ in range(tree_count - len(self.TreeSeeds))]

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

        root_nodes:list[MCTSNode] = []
        for t in range(self.TreeCount):
            node = MCTSNode(None, None)  # root has no parent
            node.ExpandRoot(self.GameState, self.PossibleMoves)
            root_nodes.append(node)  # ;root has no parent

        for i in range(max_iterations):  # selection, expansion, simulation(Playout), backpropagation
            for head, seed in zip(root_nodes, self.TreeSeeds):
                if self.EarlyStopping or self.CheckForEarlyStopping(start_time, given_time_ms):
                    PrintLog("MCTS",
                             f"Early stopping at iteration {i + 1}/{max_iterations}, elapsed time: {int(self.ElapsedTimeMs)}/{given_time_ms - 150} ms",
                             2)
                    break

                # Selection
                selected_child_node = SelectChild(head.Children)
                while selected_child_node is not None and (selected_child_node.IsExpanded() or selected_child_node.IsTerminal()):
                    selected_child_node = SelectChild(selected_child_node.GenIncompleteChildren())

                if selected_child_node is None:
                    PrintLog("MCTS",f"the tree is fully explored, stopping at iteration {i + 1}/{max_iterations}, elapsed time: {int(self.ElapsedTimeMs)}/{given_time_ms - 150} ms",2)
                    break

                # Expansion
                child = selected_child_node.ProgressiveExpand(seed)

                # Simulation and Backpropagation
                terminal_game_state = Playout(child, self.EvaluationFunction, seed)
                utilityValue = self.EvaluationFunction(terminal_game_state)
                Backpropagate(child, utilityValue)

        # mediate the results of all trees
        utilities = []
        for root_node in root_nodes:
            child_utilities = [child.AverageUtility for child in root_node.Children]
            utilities.append(child_utilities)
        utilities=np.array(utilities)
        avg_utilities = np.mean(utilities, axis=0)
        max_idex = np.argmax(avg_utilities)
        return self.PossibleMoves[max_idex]


