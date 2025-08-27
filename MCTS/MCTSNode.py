import random
from typing import Callable

from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import obtain_move_semantic_id
from MCTS.Common import calculate_ucb


class MCTSNode:
    def __init__(self, parent: 'MCTSNode', move:BasicMove, moveSeed: int | None = None):
        self.GameStates: dict[int | None, GameState] = {}
        self.ParentNode: MCTSNode | None = parent
        self.Move: BasicMove | None = move
        self.MoveSemanticId: tuple | None = obtain_move_semantic_id(self.Move)
        self.MoveSeed: int | None     = moveSeed
        self.Children: list[MCTSNode] = []
        self.UnexpandedPossibleMoves: list[BasicMove] = []

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
    def GenerateNextState(self, seed: int|None = None) -> tuple[GameState, list[BasicMove]]:
        parent_state = self.ParentNode.GameStates.get(self.MoveSeed)
        if parent_state is None:
            raise ValueError(f"No GameState available for seed {seed}")
        return parent_state.apply_move(self.Move, seed)

    def Ucb1Value(self) -> float:
        if self.ParentNode is None:
            raise ValueError("Parent node is not set, cannot calculate UCB1 value on the root node")
        return calculate_ucb(self.TotalUtility, self.NumberOfVisits, self.ParentNode.NumberOfVisits)

    #=========================Tree Structure========================
    def AddChild(self, child_node: 'MCTSNode') -> None:
        self.Children.append(child_node)

    def AddChildMove(self, move: BasicMove, seed:int|None = None) -> 'MCTSNode':
        child_node = MCTSNode(parent=self, move=move, moveSeed=seed)
        self.Children.append(child_node)
        return child_node

    def ExpandRoot(self, game_state: GameState, possible_moves: list[BasicMove]) -> None:
        self.GameStates[None] = game_state
        for move in possible_moves:
            _ = self.AddChildMove(move, None)

    def Expand(self, seed: int | None = None) -> list['MCTSNode']:
        if seed in self.GameStates:
            raise ValueError("seed already preset cannot expand again")
        node_generated = []
        self.GameStates[seed], possible_moves = self.GenerateNextState(seed)
        for move in self.GetChildrenNotAlreadyConsidered(possible_moves):
            node = self.AddChildMove(move, seed)
            node_generated.append(node)
        return node_generated

    def ProgressiveExpand(self, seed: int | None = None) -> 'MCTSNode':
        if seed not in self.GameStates:
            self.GameStates[seed], newUnexpandedPossibleMoves = self.GenerateNextState(seed)
            self.UnexpandedPossibleMoves += self.GetChildrenNotAlreadyConsidered(newUnexpandedPossibleMoves)
        if len(self.UnexpandedPossibleMoves) == 0:
            return None
        move = random.choice(self.UnexpandedPossibleMoves)
        self.UnexpandedPossibleMoves.remove(move)
        return self.AddChildMove(move,seed)

    def IsExpanded(self, times:int=1) -> bool:
        return  len(self.GameStates.keys()) >= times and len(self.UnexpandedPossibleMoves) == 0

    def IsComplete(self, max_expansion: int = 1) -> bool:
        if not self.IsComplete_value:
            self.IsComplete_value = (
                    self.IsTerminal() or
                    ( self.IsExpanded(max_expansion))
                    and all(child.IsTerminal() or child.IsComplete(max_expansion) for child in self.Children))
        return self.IsComplete_value

    def GenIncompleteChildren(self,max_expansion:int = 1 ) -> list['MCTSNode']:
        return [c for c in self.Children if not c.IsComplete(max_expansion)]

    def GetChildrenNotAlreadyConsidered(self, possible_move: list[BasicMove]) -> list[BasicMove]:
        considered_semantic_ids = [child.MoveSemanticId for child in self.Children]
        considered_semantic_ids += [obtain_move_semantic_id(m) for m in self.UnexpandedPossibleMoves]
        return [m for m in possible_move if obtain_move_semantic_id(m) not in considered_semantic_ids]


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
