import random
import numpy as np
import os
import csv
from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import NewPossibleMoveAvailable, CheckForGoalState, IsPriorMoves, MakePriorChoice
from BotCommon.Heuristics import GameStateEvaluatorUtility
from Helper.Logging import LogEndOfGame
from HeuristicLearning import RESULTS_PATH


class BoundedDS(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name: str, depth:int, evaluation_function:GameStateEvaluatorUtility, weights:np.ndarray=None, functions:list[str] = None, use_prior_move: bool = False, seed=None):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.depth: int = depth
        self.evaluation_function =  evaluation_function
        self.Weights = weights
        self.Functions = functions
        self.UsePriorMove = use_prior_move
        self.seed = seed

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick

    ## ========================Functionality========================
    def ExploreMoveAvailable(self, possible_moves:list[BasicMove], game_state:GameState) -> BasicMove:
        if not NewPossibleMoveAvailable(possible_moves):
            # if there are no moves possible, select the end of turn move
            return possible_moves[0]

        best_move = None
        best_move_val = float("-inf")
        for evaluating_move in possible_moves:
            if evaluating_move.command == MoveEnum.END_TURN:
                # skip the END_TURN command
                continue

            curr_val = self.EvaluateMove(evaluating_move, game_state, self.depth-1)
            if curr_val == float('inf'):
                # Goal State founded can return early
                return evaluating_move
            elif best_move_val < curr_val:
               best_move_val = curr_val
               best_move = evaluating_move

        return best_move

    def EvaluateMove(self,move, game_state, depth:int)->float:
        # Move Evaluation (Depth first approach)
        local_game_state, new_moves = game_state.apply_move(move,self.seed)

        if CheckForGoalState(local_game_state,self.player_id):
            return float('inf')

        if depth == 0 or not NewPossibleMoveAvailable(new_moves):
            return self.UtilityFunction(local_game_state)

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        return max(move_value)

    def UtilityFunction(self, game_state: GameState) -> float:
        return self.evaluation_function(game_state, self.Weights, self.Functions)

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        # Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if self.UsePriorMove:
            for move in possible_moves:
                if IsPriorMoves(move):
                    return move

            best_choice = MakePriorChoice(game_state, possible_moves, self.UtilityFunction)
            if best_choice is not None:
                return best_choice

        # Move Evaluation
        best_move = self.ExploreMoveAvailable(possible_moves, game_state)

        # End of Search
        if best_move is None:
            best_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            print("unexpected game state, returning end of turn")

        return best_move

    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name, end_game_state, final_state)

        won = 1 if self.player_id == final_state.current_player.player_id else 0

        file = os.path.join(RESULTS_PATH, f'{self.bot_name}_res.csv')
        with open(file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([self.bot_name, won])