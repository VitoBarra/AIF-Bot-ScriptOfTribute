import random
import time
from math import floor
from typing import Any

import numpy as np
from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import IsPriorMoves, MakePriorChoice
from MCTS import MonteCarloTreeSearch
from Helper.Logging import LogEndOfGame
from BotCommon.Heuristics import CalculateWeightedUtility_MMHVR, utilityFunction_PrestigeAndPower


class AIFBotMCTS(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name, seed=None, weights=None, functions=None):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.best_moves:list[BasicMove] = []
        self.seed = seed if seed is not None else random.randint(0, 2**64)
        self.Weights = weights
        self.Functions =functions

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick


    ## ========================Functionality========================
    @staticmethod
    def depth_sample(game_state: GameState, possible_moves:list[BasicMove]) -> tuple[int, list[Any]]:
        current_game_state = game_state
        current_possible_moves = possible_moves
        sample_branching_factors= []

        while len(current_possible_moves)>1:
            sample_branching_factors.append(len(current_possible_moves))
            current_possible_moves = [move for move in current_possible_moves if move.command != MoveEnum.END_TURN]
            current_possible_move = random.choice(current_possible_moves)
            current_game_state, current_possible_moves = current_game_state.apply_move(current_possible_move)


        return len(sample_branching_factors), sample_branching_factors

    @staticmethod
    def estimate_depth(game_state: GameState, possible_moves:list[BasicMove]) -> tuple[int, Any]:
        max_sample_depth = 0
        bs = []
        for i in range(100):
            sample_depth, sample_branching_factors = AIFBotMCTS.depth_sample(game_state, possible_moves)
            bs.append(sample_branching_factors)
            if sample_depth > max_sample_depth:
                max_sample_depth = sample_depth

        # mediate on branching factors
        bs = [np.array(x) for x in bs]
        max_len = max(len(x) for x in bs)
        bs_padded = np.array([np.pad(x, (0, max_len - len(x))) for x in bs])
        bs_masked = np.where(bs_padded == 0, np.nan, bs_padded)
        mean = np.nanmean(bs_masked, axis=0).astype(float).tolist()

        return max_sample_depth, mean


    def CalculateWeightedUtility_MMHVR(self, game_state: GameState) -> float:
        return CalculateWeightedUtility_MMHVR(game_state,self.Weights,self.Functions)

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

        best_choice = MakePriorChoice(game_state, possible_moves, self.CalculateWeightedUtility_MMHVR)
        if best_choice is not None:
            print(f"    Prior choice found:  {best_choice.command}")
            return best_choice


        #Move Evaluation
        start_time = time.perf_counter()
        # monte_carlo_tree_search = MonteCarloTreeSearch(game_state, possible_moves, floor(remaining_time/len(possible_moves)), utilityFunction_PrestigeAndPower, 500)
        monte_carlo_tree_search = MonteCarloTreeSearch(game_state, possible_moves, floor(remaining_time/len(possible_moves)), self.CalculateWeightedUtility_MMHVR, 500)
        best_move = monte_carlo_tree_search.MonteCarloSearch()
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

