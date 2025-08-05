import random
from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import PlayerEnum, MoveEnum


from BotCommon.CommonCheck import NewPossibleMoveAvailable, CheckForGoalState
from BotCommon.Heuristics import utilityFunction_PrestigeAndPower
from Helper.Logging import LogEndOfGame


class MaxPrestigeSettableDepthBot(BaseAI):

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
    def ExploreMoveAvailable(self, possible_moves, game_state):
        if not NewPossibleMoveAvailable(possible_moves):
            # If there are no moves possible, select the end of turn move
            return possible_moves[0]

        best_move = None
        best_move_val = float("-inf")
        for evaluating_move in possible_moves:
            if evaluating_move.command == MoveEnum.END_TURN:
                # Skip the END_TURN command
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
        if CheckForGoalState(local_game_state,self.player_id):
            return float('inf')

        if depth == 0 or not NewPossibleMoveAvailable(new_moves):
            return utilityFunction_PrestigeAndPower(local_game_state)

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        return max(move_value)

    def play(self, game_state, possible_moves, remaining_time):
        # Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        # Move Evaluation
        bast_move = self.ExploreMoveAvailable(possible_moves, game_state)

        # End of Search
        if bast_move is None:
            bast_move = next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
            print("unexpected game state, returning end of turn")

        return bast_move

    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        LogEndOfGame(self.bot_name,end_game_state, final_state)
