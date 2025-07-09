import os
import random

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove

from BotCommon.CommonCheck import NewPossibleMoveAvailable, CheckForGoalState
from BotCommon.Heuristics import utilityFunction_MIXMAXAVERAGERES


class AIFBot(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name,depth):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.depth: int = depth
        self.best_moves:list[BasicMove] = []


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

            curr_val = self.EvaluateMove(evaluating_move,game_state,self.depth-1)
            if curr_val == float('inf'):
                # Goal State founded can return early
                return evaluating_move
            elif best_move_val < curr_val:
               best_move_val = curr_val
               best_move = evaluating_move

        return best_move

    def EvaluateMove(self,move, game_state, depth:int)->float:
        # Move Evaluation (Depth first approach)
        local_game_state, new_moves = game_state.apply_move(move)

        if CheckForGoalState(local_game_state,self.player_id):
            return float('inf')

        if depth == 0 or not NewPossibleMoveAvailable(new_moves):
            return utilityFunction_MIXMAXAVERAGERES(local_game_state)

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        return max(move_value)

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        #Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        #Move Evaluation
        bast_move = self.ExploreMoveAvailable(possible_moves, game_state)

        # End of Search
        if bast_move is None:
            bast_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            print("unexpected game state, returning end of turn")

        return bast_move

    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        # Example how you can log your game for further analysis
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        filename = f"game_log_{final_state.state_id}_{end_game_state.winner}.log"
        filepath = os.path.join(log_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"=== Game Ended ===\n")
                f.write(f"Winner: {end_game_state.winner}\n")
                f.write(f"Reason: {end_game_state.reason}\n")
                f.write(f"Context: {end_game_state.AdditionalContext}\n\n")
                f.write("=== Completed Actions ===\n")

                for action in final_state.completed_actions:
                    f.write(action + "\n")

            print(f"[INFO] Game log saved to: {filepath}")

        except Exception as e:
            print(f"[ERROR] Failed to save game log: {e}")

