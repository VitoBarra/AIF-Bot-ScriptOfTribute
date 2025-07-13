import random
from math import floor

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import IsPriorMoves
from MCTS import MonteCarloTreeSearch
from BotCommon.Logging import LogEndOfGame
from BotCommon.Heuristics import utilityFunction_MMHVR

class AIFBotMCTS(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.best_moves:list[BasicMove] = []

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick


    ## ========================Functionality========================
    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        #Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if len(possible_moves) == 1 and possible_moves[0].command == MoveEnum.END_TURN:
            return possible_moves[0]

        for move in possible_moves:
            if IsPriorMoves(move,game_state):
                # Return the first prior move encountered
                return move

        #Move Evaluation
        monte_carlo_tree_search = MonteCarloTreeSearch(game_state, possible_moves, floor(remaining_time/len(possible_moves)), utilityFunction_MMHVR,500)
        best_move = monte_carlo_tree_search.MonteCarloSearch()

        # End of Search
        if best_move is None:
            best_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            print("best_move was None, returning end of turn")

        return best_move

    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name,end_game_state, final_state)

