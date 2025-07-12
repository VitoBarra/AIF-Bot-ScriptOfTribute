import os
import random
import re

import numpy as np

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import PatronId, MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove, SimpleCardMove, SimplePatronMove

from BotCommon.CommonCheck import NewPossibleMoveAvailable, CheckForGoalState, MatchCommand
from BotCommon.Heuristics import utilityFunction_MIXMAXAVERAGERES
from BotCommon.Logging import LogEndOfGame


class AIFBotMoveSaving(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name,depth, seed=None):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.depth: int = depth
        self.best_moves:list[BasicMove] = []
        self.seed = seed if seed is not None else random.randint(0, 2**64)

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick


    ## ========================Functionality========================
    def ExploreMoveAvailable(self, possible_moves:list[BasicMove], game_state:GameState) ->list[BasicMove]:
        if not NewPossibleMoveAvailable(possible_moves):
            # If there are no moves possible, select the end of turn move
            return [next(move for move in possible_moves if move.command == MoveEnum.END_TURN)]

        best_moves = None
        best_moves_val = float("-inf")
        for evaluating_move in possible_moves:
            if evaluating_move.command == MoveEnum.END_TURN:
                # Skip the END_TURN command
                continue

            curr_val, moves = self.EvaluateMove(evaluating_move,game_state,self.depth-1)
            if curr_val == float('inf'):
                # Goal State found, can return early
                return moves
            elif best_moves_val < curr_val:
               best_moves_val = curr_val
               best_moves = moves

        return best_moves if best_moves is not None else []

    def EvaluateMove(self,move, game_state, depth:int)->(float, list[BasicMove]):
        # Move Evaluation (Depth first approach)
        local_game_state, new_moves = game_state.apply_move(move,self.seed)

        if CheckForGoalState(local_game_state,self.player_id):
            return float('inf'), [move]

        if depth == 0 or not NewPossibleMoveAvailable(new_moves):
            return utilityFunction_MIXMAXAVERAGERES(local_game_state), [move]

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        max_value, list_of_move = max(move_value, key=lambda x: x[0], default=(0, []))

        if len (list_of_move)==0:
            print ("legal move list is empty")

        return max_value , [move] + list_of_move

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        # Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if len(self.best_moves)<=0:
            # Move Evaluation
            self.best_moves = self.ExploreMoveAvailable(possible_moves, game_state)

        best_move:BasicMove = MatchCommand(self.best_moves.pop(), possible_moves)


        if best_move in possible_moves:
            print(f"played:  {best_move.command}: {best_move.move_id}")
            if best_move.command == MoveEnum.BUY_CARD:
                # Recalculate the best move after a non-deterministic move
                self.best_moves = []
            return best_move
        elif best_move is None:
            print("unexpected game state, returning end of turn")
            return next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
        else:
            print(f"tried to do an illegal move {best_move.command}: {best_move.move_id}")
            return next(move for move in possible_moves if move.command == MoveEnum.END_TURN)


    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name,end_game_state, final_state)