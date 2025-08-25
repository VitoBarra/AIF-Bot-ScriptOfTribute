import random
import time
from typing import Callable

from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove

from MCTS.MCTSNode import MCTSNode


class FlatMCTS:
    early_stopping_time = 0

    def __init__(self, game_state: GameState, possible_moves: list[BasicMove], eval_function : Callable):
        self.RootNode = MCTSNode(None, possible_moves, game_state) # root has no parent
        self.EvaluationFunction = eval_function
        self.ListOfLeafNodes: list[MCTSNode] = []
        for move in possible_moves:
            child_node = self.RootNode.AddChildMove(move)
            self.ListOfLeafNodes.append(child_node)

    def SelectChild(self) -> MCTSNode:
        ucb1s = {child:child.Ucb1Value() for child in self.ListOfLeafNodes}
        # get the child with the highest ucb1 value
        return  max(ucb1s, key=ucb1s.get)


    #=========================Playout Policies========================
    @staticmethod
    def playout_policy_random(possible_move:list[BasicMove]) -> BasicMove:
        return random.choice(possible_move)

    @staticmethod
    def playout_policy_greedy_heuristic(game_state:GameState, possible_move:list[BasicMove], eval_function:Callable) -> BasicMove:
        move_value = {m: float('-inf') for m in possible_move}
        for move in possible_move:
            gs1, _ = game_state.apply_move(move)
            val = eval_function(gs1)
            if val > move_value[move]:
                move_value[move] = val
        return max(move_value, key=move_value.get)

    @staticmethod
    def playout_policy_greedy_heuristic_lookAhead(game_state:GameState, possible_move:list[BasicMove], eval_function:Callable) -> BasicMove:
        move_value = {m: float('-inf') for m in possible_move}
        for move in possible_move:
            gs1, ps1 = game_state.apply_move(move)
            for move2 in ps1:
                gs2, _ = gs1.apply_move(move2)
                val = eval_function(gs2)
                if val > move_value[move]:
                    move_value[move] = val

        return max(move_value, key=move_value.get)

    @staticmethod
    def Playout(selected_node: MCTSNode, eval_function:Callable) -> float:
        currentGameState, currentPossibleMove = selected_node.ExpandNode()
        while not len(currentPossibleMove)<=1 and currentPossibleMove[0].command != MoveEnum.END_TURN:
            # randomly select semple the non-deterministic state space
            selected_move = FlatMCTS.playout_policy_random(currentPossibleMove)
            # selected_move = FlatMCTS.playout_policy_greedy_heuristic(CurrentGameState,CurrentPossibleMove,eval_function)
            # selected_move = FlatMCTS.playout_policy_greedy_heuristic_lookAhead(CurrentGameState,CurrentPossibleMove,eval_function)
            currentGameState, currentPossibleMove = currentGameState.apply_move(selected_move)

        return eval_function(currentGameState)

    ##=========================Backpropagation========================
    @staticmethod
    def Backpropagate(node:MCTSNode, utilityValue:float) -> None:
        node.NumberOfVisits += 1
        # Update the average value and max value
        node.AverageUtility += (utilityValue - node.AverageUtility) / node.NumberOfVisits
        # Update the max value
        node.max_val = utilityValue if utilityValue > node.MaxUtility else node.MaxUtility

        if node.ParentNode is not None:
            FlatMCTS.Backpropagate(node.ParentNode, utilityValue)  # Parent is not a leaf

    #=========================MCTS Main Function========================
    def MonteCarloSearch(self, max_iteration:int, given_time_ms:int) -> BasicMove:
        start_time = time.perf_counter()

        for i in range(max_iteration): #selection, expansion, simulation(Playout), backpropagation
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000
            if given_time_ms - elapsed_time_ms >  150:
                break

            selected_child_node:MCTSNode = self.SelectChild()
            # EXPANSION is skipped in FlatMCTS, we only have one layer of children
            utilityValue = FlatMCTS.Playout(selected_child_node, self.EvaluationFunction)
            FlatMCTS.Backpropagate(selected_child_node,utilityValue)

        best_move = max(self.RootNode.Children, key=lambda c: (c.MaxUtility, c.NumberOfVisits))
        if best_move.ParentMove.command == MoveEnum.END_TURN and len(self.RootNode.Children) > 1:
            FlatMCTS.early_stopping_time += 1

        return best_move.ParentMove


