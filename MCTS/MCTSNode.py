from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove

from MCTS.Common import calculate_ucb


class MCTSNode:
    def __init__(self, parent: 'MCTSNode', parent_move, game_state: GameState = None):
        self.GameState: GameState = game_state
        self.ParentNode: MCTSNode|None = parent
        self.ParentMove: BasicMove = parent_move
        self.Children: list[MCTSNode] = []

        self.NumberOfVisits = 0 # N(n)
        self.MaxUtility = 0 # U(n)
        self.AverageUtility = 0.0 # Q(n), average value of the node


    ##=========================Node kind check========================
    def IsLeaf(self):
        return len(self.Children) == 0

    def IsTerminal(self) -> bool:
        return self.ParentMove.command == MoveEnum.END_TURN

    ##===============================================================
    def ExpandNode(self, seed: int | None = None) -> tuple[GameState, list[BasicMove]]:
        self.GameState, possible_moves = self.ParentNode.GameState.apply_move(self.ParentMove, seed)  # Apply the move to the game state
        return self.GameState, possible_moves

    def Ucb1Value(self) -> float:
        if self.ParentNode is None:
            raise ValueError("Parent node is not set, cannot calculate UCB1 value on the root node")
        return calculate_ucb(self.MaxUtility, self.ParentNode.NumberOfVisits, self.AverageUtility)

    #=========================Tree Structure========================
    def AddChild(self, child_node: 'MCTSNode'):
        self.Children.append(child_node)

    def AddChildMove(self, move: BasicMove):
        child_node = MCTSNode(parent=self, parent_move=move)
        self.Children.append(child_node)
        return child_node





