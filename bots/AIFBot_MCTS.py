import random
import time
from math import floor

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import IsPriorMoves, MakePriorChoice
from Helper.Logging import LogEndOfGame

from MCTS.mcts2 import MCTS2

class AIFBotMCTS(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name, evaluation_function, weights=None, functions=None):
        super().__init__(bot_name)
        self.evaluation_function = evaluation_function
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.best_moves:list[BasicMove] = []
        self.Weights   = weights
        self.Functions = functions

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick


    ## ========================Functionality========================
    def UtilityFunction(self, game_state: GameState) -> float:
        return self.evaluation_function(game_state, self.Weights, self.Functions, self.player_id)

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        #Set Up
        print(f"star time: {remaining_time} ms possible moves: {len(possible_moves)}")
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if len(possible_moves) == 1 and possible_moves[0].command == MoveEnum.END_TURN:
            print("===============[End of turn]================")
            return possible_moves[0]

        for move in possible_moves:
            if IsPriorMoves(move):
                # Return the first prior move encountered
                print(f"    Prior move   found:  {move.command}")
                return move

        best_choice = MakePriorChoice(game_state, possible_moves, self.UtilityFunction)
        if best_choice is not None:
            print(f"    Prior choice found:  {best_choice.command}")
            return best_choice


        #Move Evaluation
        start_time = time.perf_counter()
        # monte_carlo_tree_search = MonteCarloTreeSearch(game_state, possible_moves, floor(remaining_time/len(possible_moves)), self.UtilityFunction, 500)
        # best_move = monte_carlo_tree_search.MonteCarloSearch()

        monte_carlo_tree_search = MCTS2(game_state, possible_moves, remaining_time, self.player_id, self.UtilityFunction)
        best_move = monte_carlo_tree_search.move_choice(500)

        elapsed_time_ms = (time.perf_counter() - start_time) * 1000
        print(f"MONTE CARLO SELECTION Elapsed:")
        print(f"    time: {elapsed_time_ms} ms, remining time: {remaining_time} ms")
        print(f"    state: coin {game_state.current_player.coins}, prestige: {game_state.current_player.prestige}, power: {game_state.current_player.power}")
        print(f"    best move selected MC: {best_move.command}")


        # End of Search
        if best_move is None:
            best_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            print("best_move was None, returning end of turn")

        return best_move

    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name,end_game_state, final_state)

