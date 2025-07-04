import random
import os

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import EndGameState, GameState
from scripts_of_tribute.enums import PlayerEnum, MoveEnum

class MaxPrestigeBot(BaseAI):

    def __init__(self, bot_name):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
    
    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick
    
    def play(self, game_state, possible_moves, remaining_time):
        best_move = None
        best_move_val = -99
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        for first_move in possible_moves:
            if first_move.command == MoveEnum.END_TURN:
                continue
            new_game_state, new_moves = game_state.apply_move(first_move)

            if new_game_state.end_game_state is not None:  # check if game is over, if we win we are fine with this move
                if new_game_state.end_game_state.winner == self.player_id:
                    return first_move

            if len(new_moves) == 1 and new_moves[0].command == MoveEnum.END_TURN:  # if there are no moves possible then lets just check value of this game state
                curr_val = new_game_state.current_player.prestige + new_game_state.current_player.power
                if curr_val > best_move_val:
                    best_move = first_move
                    best_move_val = curr_val

            for second_move in new_moves:
                if second_move.command == MoveEnum.END_TURN:
                    continue
                final_game_state, _ = new_game_state.apply_move(second_move)
                if final_game_state.end_game_state is not None:
                    if final_game_state.end_game_state.winner == self.player_id:
                        return first_move
                curr_val = final_game_state.current_player.prestige + final_game_state.current_player.power
                if curr_val > best_move_val:
                    best_move = first_move
                    best_move_val = curr_val
        if best_move is None:
            return next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
        return best_move
    
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