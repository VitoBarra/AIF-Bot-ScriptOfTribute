import time
from typing import Callable

from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove

from Helper.Logging import PrintLog
from MCTS.MCTSNode import MCTSNode, Backpropagate, Playout, SelectChild


class FlatMCTS:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove], eval_function : Callable):
        self.GameState = game_state
        self.EvaluationFunction = eval_function
        self.PossibleMoves = possible_moves
        self.EarlyStopping = False
        self.ElapsedTimeMs = 0


    def CheckForEarlyStopping(self, start_time: float, given_time_ms: int, buffer_time:int = 150) -> bool:
        self.ElapsedTimeMs = (time.perf_counter() - start_time) * 1000
        self.EarlyStopping = given_time_ms - self.ElapsedTimeMs < buffer_time
        return self.EarlyStopping

    #=========================MCTS Main Function========================
    def MonteCarloSearch(self, max_iterations:int, given_time_ms:int) -> BasicMove:
        PrintLog("MCTS", f"Starting MCTS with {max_iterations} iterations and {given_time_ms} ms time limit", 2)
        start_time = time.perf_counter()

        root_node = MCTSNode(None, None)  # ;root has no parent
        root_node.ExpandRoot(self.GameState, self.PossibleMoves)

        for i in range(max_iterations): #selection, expansion, simulation(Playout), backpropagation

            if self.CheckForEarlyStopping(start_time, given_time_ms):
                PrintLog("MCTS", f"Early stopping at iteration {i+1}/{max_iterations}, elapsed time: {int(self.ElapsedTimeMs)}/{given_time_ms-150} ms", 2)
                break

            # Selection
            selected_child_node = SelectChild(root_node.Children)
            # EXPANSION is skipped in FlatMCTS, we only have one layer of children
            # Simulation and Backpropagation
            terminal_game_state = Playout(selected_child_node, self.EvaluationFunction)
            utilityValue = self.EvaluationFunction(terminal_game_state)
            Backpropagate(selected_child_node,utilityValue)

        best_move = max(root_node.Children, key=lambda c: (c.AverageUtility, c.NumberOfVisits))
        return best_move.Move



