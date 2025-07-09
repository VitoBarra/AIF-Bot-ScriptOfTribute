import numpy as np

from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove
from AIFBot import AIFBot

def some_time_left() -> bool:
    return True # NEEDS TO BE IMPLEMENTED

class MonteCarloTreeSearchNode:
    def __init__(self, game_state: GameState, parent=None, parent_move=None, untried_moves=None):
        self.game_state: GameState = game_state # it can be obtained with apply_move from the parent game_state
        self.parent: MonteCarloTreeSearchNode = parent
        self.parent_move: BasicMove = parent_move
        if untried_moves is None:
            self.untried_moves: list[BasicMove] = []
        self.children: list[MonteCarloTreeSearchNode] = []
        self.number_of_visits = 0 # N(n)
        self.max_val = 0 # U(n)
        self.is_leaf = True

    def has_untried_move(self) -> bool:
        return len(self.untried_moves) > 0

    def child_node_selection(self):
        c = np.sqrt(2) # In Theory it must be root(2) but we can test other parameters
        best_ucb1 = 0
        best_child_node = None # should be MonteCarloTreeSearchNode

        for child_node in self.children:

            if child_node.is_leaf or child_node.number_of_visits == 0:
                return child_node

            exploitation_term = child_node.max_val/child_node.number_of_visits
            exploration_term = np.sqrt(np.log(self.number_of_visits)/child_node.number_of_visits)
            ucb1 = exploitation_term + c * exploration_term

            if ucb1 > best_ucb1:
                best_ucb1 = ucb1
                best_child_node = child_node

        if best_child_node is None:
            raise ValueError("No Node selected")

        return best_child_node
    
    def node_expansion(self):
        while self.has_untried_move():
            untried_move: BasicMove = self.untried_moves.pop()
            child_game_state, child_moves = self.game_state.apply_move(untried_move)
            child_node = MonteCarloTreeSearchNode(child_game_state, self, untried_move, child_moves)
            self.children.append(child_node)
            
    def playout(self): # Must return a MonteCarloTreeSearchNode
        terminal_node = None
        # NEEDS TO BE IMPLEMENTED
        # return terminal_node
        return self
    
    def evaluate_terminal_node (self, aif_bot: AIFBot):
        return aif_bot.utilityFunction(self.game_state)

    def backpropagate(self, val, is_leaf = True):
        self.number_of_visits += 1
        self.is_leaf = is_leaf
        if val > self.max_val:
            self.max_val = val # The paper says that for Tales of tribute using the max instead of the sum is better
        if self.parent:
            self.parent.backpropagate(val, False) # Parent is not a leaf

class MonteCarloTreeSearch:
    def __init__(self, game_state: GameState, possible_moves: list[BasicMove]):
        self.root = MonteCarloTreeSearchNode(game_state, None, None, possible_moves) # root has no parent
        self.root.node_expansion()
        self.aif_bot = AIFBot("utility_function", 0)
        
    def move_choice(self): # si potrebbe chiamare play ma non vorrei fare confusione con la funzione play del bot

        while some_time_left():
            selected_child_node = self.root.child_node_selection()
            if selected_child_node.is_leaf:
                terminal_node: MonteCarloTreeSearchNode = selected_child_node.playout()
                val = terminal_node.evaluate_terminal_node(self.aif_bot)
                terminal_node.backpropagate(val)
                
        max_val = -1
        move = None
                
        for child in self.root.children:
            if child.max_val > max_val:
                max_val = child.max_val
                move = child.parent_move
                
        return move