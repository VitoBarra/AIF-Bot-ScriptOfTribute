import random
from typing import Callable

from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove

from MCTS.Common import calculate_ucb


class MCTSNode:
    def __init__(self, parent: 'MCTSNode', move:BasicMove):
        self.GameState: GameState = None
        self.ParentNode: MCTSNode | None = parent
        self.Move: BasicMove | None = move
        self.Children: list[MCTSNode] = []

        self.NumberOfVisits = 0
        self.MaxUtility     = 0
        self.AverageUtility = 0.0
        self.TotalUtility   = 0.0

        self.IsComplete_value = False

    ##=========================Node kind check========================
    def IsLeaf(self):
        return len(self.Children) == 0

    def IsTerminal(self) -> bool:
        return self.Move.command == MoveEnum.END_TURN

    ##===============================================================
    def GenerateNextState(self, seed: int | None = None) -> tuple[GameState, list[BasicMove]]:
        game_state, possible_moves = self.ParentNode.GameState.apply_move(self.Move, seed)  # Apply the move to the game state
        return game_state, possible_moves

    def Ucb1Value(self) -> float:
        if self.ParentNode is None:
            raise ValueError("Parent node is not set, cannot calculate UCB1 value on the root node")
        return calculate_ucb(self.TotalUtility, self.NumberOfVisits, self.ParentNode.NumberOfVisits)

    #=========================Tree Structure========================
    def AddChild(self, child_node: 'MCTSNode') -> None:
        self.Children.append(child_node)

    def AddChildMove(self, move: BasicMove) -> 'MCTSNode':
        child_node = MCTSNode(parent=self, move=move)
        self.Children.append(child_node)
        return child_node

    def ExpandRoot(self, game_state: GameState, possible_moves: list[BasicMove]) -> None:
        self.GameState = game_state
        for move in possible_moves:
            _ = self.AddChildMove(move)

    def Expand(self, seed: int | None = None) -> list['MCTSNode']:
        if self.GameState is not None:
            raise ValueError("already fully expanded node cannot be expanded again")
        node_generated = []
        self.GameState, possible_moves = self.GenerateNextState(seed)
        for move in possible_moves:
            node = self.AddChildMove(move)
            node_generated.append(node)
        return node_generated

    def IsExpanded(self) -> bool:
        return len(self.Children) > 0

    def IsComplete(self):
        if not self.IsComplete_value:
            self.IsComplete_value = (
                    self.IsTerminal() or
                    (self.IsExpanded()
                    and all(child.IsTerminal() or child.IsComplete() for child in self.Children)))
        return self.IsComplete_value

    def GenIncompleteChildren(self) -> list['MCTSNode']:
        return [c for c in self.Children if not c.IsComplete()]


#=========================Selection========================
def SelectChild(ListOfLeafNodes:list[MCTSNode]) -> MCTSNode | None:
    if len(ListOfLeafNodes) == 0:
        return None
    ucb1s = {child:child.Ucb1Value() for child in ListOfLeafNodes}
    max_val = max(ucb1s.values())
    best = [c for c, v in ucb1s.items() if v == max_val]
    return random.choice(best)


#=========================Playout Policies========================
def playout_policy_random(possible_moves:list[BasicMove]) -> BasicMove:
    filter = [m for m in possible_moves if m.command != MoveEnum.END_TURN]
    if len(filter) == 0:
        return possible_moves[0]
    return random.choice(filter)


def playout_policy_greedy_heuristic(game_state:GameState, possible_move:list[BasicMove], eval_function:Callable, seed:int|None = None) -> BasicMove:
    move_value = {m: float('-inf') for m in possible_move}
    for move in possible_move:
        gs1, _ = game_state.apply_move(move,seed)
        val = eval_function(gs1)
        if val > move_value[move]:
            move_value[move] = val
    return max(move_value, key=move_value.get)

def playout_policy_greedy_heuristic_lookAhead(game_state:GameState, possible_move:list[BasicMove], eval_function:Callable, seed:int|None = None) -> BasicMove:
    move_value = {m: float('-inf') for m in possible_move}
    for move in possible_move:
        gs1, ps1 = game_state.apply_move(move,seed)
        for move2 in ps1:
            gs2, _ = gs1.apply_move(move2,seed)
            val = eval_function(gs2)
            if val > move_value[move]:
                move_value[move] = val

    return max(move_value, key=move_value.get)

def Playout(selected_node: MCTSNode, eval_function:Callable, seed: int | None = None) -> GameState:
    random.seed(seed)
    currentGameState, currentPossibleMove = selected_node.GenerateNextState(seed)
    while not len(currentPossibleMove)<=1 and currentPossibleMove[0].command != MoveEnum.END_TURN:
        # randomly select semple the non-deterministic state space
        selected_move = playout_policy_random(currentPossibleMove)
        # selected_move = playout_policy_greedy_heuristic(currentGameState,currentPossibleMove,eval_function,seed=seed)
        # selected_move = playout_policy_greedy_heuristic_lookAhead(currentGameState,currentPossibleMove,eval_function,seed=seed)
        currentGameState, currentPossibleMove = currentGameState.apply_move(selected_move)

    return currentGameState

##=========================Backpropagation========================
def Backpropagate(node:MCTSNode, utilityValue:float) -> None:
    node.NumberOfVisits += 1
    # Update the average value and max value
    node.AverageUtility += (utilityValue - node.AverageUtility) / node.NumberOfVisits
    # Update the max value
    node.MaxUtility = utilityValue if utilityValue > node.MaxUtility else node.MaxUtility
    # update the total value
    node.TotalUtility += utilityValue

    if node.ParentNode is not None:
        Backpropagate(node.ParentNode, utilityValue)
