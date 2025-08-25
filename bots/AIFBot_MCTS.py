import random
import time
from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import IsPriorMoves, MakePriorChoice
from Helper.Logging import PrintLog
from Helper.Logging import LogEndOfGame
from MCTS.DMultyTMCTS import DMultyTCTS
from MCTS.DSingleTMCTS import DSingleTMCTS
from MCTS.FlatMCTS import FlatMCTS
from MCTS.ClassicMCTS import MCTS
from MCTS.ProgressiveMCTS import ProgressiveMCTS

from MCTS.mcts2 import MCTS2
from MCTS.Common import give_time

from enum import Enum

class MCTSenum(Enum):
    MCTS2               = 1
    FlatMCTS            = 2
    MCTS                = 3
    ProgressiveMCTS     = 4
    DMultyTMCTS             = 5
    DSingleTMCTS             = 6


class AIFBotMCTS(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name, evaluation_function, max_iteration = 200, weights=None, functions=None, seed=None, MCTSversion: MCTSenum = MCTSenum.MCTS2 ):
        super().__init__(bot_name)
        self.evaluation_function = evaluation_function
        self.MaxIteration = max_iteration
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.best_moves:list[BasicMove] = []
        self.seed      = seed
        self.Weights   = weights
        self.Functions = functions
        self.MCTSversion = MCTSversion

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick


    ## ========================Functionality========================
    def UtilityFunction(self, game_state: GameState) -> float:
        return self.evaluation_function(game_state, self.Weights, self.Functions, self.player_id)

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        #Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if len(possible_moves) == 1 and possible_moves[0].command == MoveEnum.END_TURN:
            AIFBotMCTS.checks_before_return(possible_moves[0], remaining_time)
            return possible_moves[0]

        for move in possible_moves:
            if IsPriorMoves(move):
                # Return the first prior move encountered
                PrintLog(f"PRIOR", f"selected move {move.command} over {len(possible_moves)} possible move with {remaining_time} ms remaining",1)
                PrintLog("STATE",
                         f"coin {game_state.current_player.coins}, prestige: {game_state.current_player.prestige}, power: {game_state.current_player.power}",
                         1)
                AIFBotMCTS.checks_before_return(move, remaining_time)
                return move

        best_choice = MakePriorChoice(game_state, possible_moves, self.UtilityFunction)
        if best_choice is not None:
            PrintLog(f"PRIOR", f"selected move {best_choice.command} over {len(possible_moves)} with {remaining_time} ms remaining",1)
            AIFBotMCTS.checks_before_return(best_choice, remaining_time)
            PrintLog("STATE",
                     f"coin {game_state.current_player.coins}, prestige: {game_state.current_player.prestige}, power: {game_state.current_player.power}",
                     1)
            return best_choice

        if len(possible_moves) > 1:
            if remaining_time < 1000:
                best_move = random.choice([m for m in possible_moves if m.command != MoveEnum.END_TURN])
            else:
                #Move Evaluation
                start_time = time.perf_counter()

                time_to_give = give_time(game_state, possible_moves, int(remaining_time * (4/5)), self.player_id)
                elapsed_time_ms = (time.perf_counter() - start_time) * 1000
                time_to_give -= int(elapsed_time_ms)

                monte_carlo_tree_search = None
                match self.MCTSversion:
                    case MCTSenum.MCTS2:
                        monte_carlo_tree_search = MCTS2(game_state, possible_moves, self.player_id,self.UtilityFunction, self.seed)
                    case MCTSenum.FlatMCTS:
                        monte_carlo_tree_search = FlatMCTS(game_state, possible_moves, self.UtilityFunction)
                    case MCTSenum.MCTS:
                        monte_carlo_tree_search = MCTS(game_state, possible_moves, self.UtilityFunction)
                    case MCTSenum.ProgressiveMCTS:
                        monte_carlo_tree_search = ProgressiveMCTS(game_state, possible_moves, self.UtilityFunction)
                    case MCTSenum.DMultyTMCTS:
                        monte_carlo_tree_search = DMultyTCTS(game_state, possible_moves, self.UtilityFunction)
                    case MCTSenum.DSingleTMCTS:
                        monte_carlo_tree_search = DSingleTMCTS(game_state, possible_moves, self.UtilityFunction)
                    case _:
                        raise ValueError("Unknown MCTS version")

                best_move = monte_carlo_tree_search.MonteCarloSearch(self.MaxIteration, time_to_give)

                elapsed_time_ms = (time.perf_counter() - start_time) * 1000
                PrintLog("MCTS",f"selected move {best_move.command} in {elapsed_time_ms:.2f} ms over the {remaining_time} ms remaining and over {len(possible_moves)} moves",1)
                PrintLog("STATE",f"coin {game_state.current_player.coins}, prestige: {game_state.current_player.prestige}, power: {game_state.current_player.power}",1)
        elif len(possible_moves) == 1:
            best_move = possible_moves[0]
            PrintLog ("MOVE",f"selected move {best_move.command}",1)
        else:
            best_move = None
            PrintLog("NO MOVE","no valid moves found", 1)

        # End of Search
        if best_move is None:
            best_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            PrintLog("MCTS","best_move was None, returning end of turn",1)

        AIFBotMCTS.checks_before_return(best_move, remaining_time)
        return best_move

    @staticmethod
    def checks_before_return(move:BasicMove, remaining_time):
        if remaining_time is not None and move.command == MoveEnum.END_TURN:
            PrintLog(f"END", f"remaining time: {remaining_time} ms", 0)


    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name,end_game_state, final_state)

