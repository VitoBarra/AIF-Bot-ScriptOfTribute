import os
import random
import numpy as np

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import PatronId, MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove


class AIFBot(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name,depth):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.depth: int = depth

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick

    ## ========================Functionality========================

    def CalculateMaxMinAverageCoin(self,game_state: GameState):
        max = 1
        average = 1
        min = 1



        return (max, average,min)

    def CalculateMaxMinAveragePowerAndPrestige(self, game_state):
        max = 1
        average = 1
        min = 1

        return (max, average, min)

    def CalculateFavor(self,game_state:GameState):
        patron_favor = game_state.patron_states.patrons.items()
        favor = 0
        for patron_id, player_enum in patron_favor:
            if player_enum == PlayerEnum.NO_PLAYER_SELECTED:
                continue # if the patron favor is neutral it will ignore
            elif player_enum == self.player_id:
                favor = favor + 1
            else:
                favor = favor - 1
        return favor

    def CalculateCoinLeft(self,game_state):
        return game_state.current_player.coins

    def utilityFunction(self, game_state):
            max_coin, average_coin, min_coin = self.CalculateMaxMinAverageCoin(game_state)
            max_PEP, average_PEP, min_PEP = self.CalculateMaxMinAveragePowerAndPrestige(game_state)
            favor = self.CalculateFavor(game_state)
            coin_left = self.CalculateCoinLeft(game_state)

            param   = np.array([np.log(max_coin), average_coin , min_coin , max_PEP**1.3, average_PEP, min_PEP, np.sign(favor) * favor**2, -coin_left])
            weight  = np.ones((1,param.shape[0])) # trained
            utility = weight @ param
            return utility[0]

    def CheckForGoalState(self, game_state) -> bool:
        if game_state.end_game_state is not None:
            # check if game is over, if we win we are fine with this move
            if game_state.end_game_state.winner == self.player_id:
                return True
        return False

    def NewPossibleMoveAviable(self, moves):
        return not (len(moves) == 1 and moves[0].command == MoveEnum.END_TURN)

    def ExploreMoveAvailable(self, possible_moves, game_state):
        if not self.NewPossibleMoveAviable(possible_moves):
            # if there are no moves possible, select the end of turn move
            return possible_moves[0]

        best_move = None
        best_move_val = float("-inf")
        for evaluating_move in possible_moves:
            if evaluating_move.command == MoveEnum.END_TURN:
                # skip the END_TURN command
                continue

            curr_val = self.EvaluateMove(evaluating_move,game_state,self.depth)
            if curr_val == float('inf'):
                # Goal State founded can return early
                return evaluating_move
            elif best_move_val < curr_val:
               best_move_val = curr_val
               best_move = evaluating_move

        return best_move

    def EvaluateMove(self,move, game_state, depth:int):
        # Move Evaluation (Depth first approach)
        local_game_state, new_moves = game_state.apply_move(move)
        if self.CheckForGoalState(local_game_state):
            return float('inf')

        if depth == 0:
            return self.utilityFunction(local_game_state)
        elif not self.NewPossibleMoveAviable(new_moves):
            # if there are no moves possible then let's just check the value of this game state
            return self.utilityFunction(local_game_state)

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        return max(move_value)

    def play(self, game_state, possible_moves, remaining_time):
        #Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        #Move Evaluation
        bast_move = self.ExploreMoveAvailable(possible_moves, game_state)

        # End of Search
        if bast_move is None:
            bast_move = MoveEnum.END_TURN
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

