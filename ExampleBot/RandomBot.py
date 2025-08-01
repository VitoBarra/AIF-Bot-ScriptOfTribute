import random

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.enums import MoveEnum


class RandomBot(BaseAI):

    def select_patron(self, available_patrons):
        return random.choice(available_patrons)

    # def play(self, game_state, possible_moves, remaining_time):
    #     pick = random.choice(possible_moves)
    #     return pick

    def play(self, game_state, possible_moves, remaining_time):
        if len(possible_moves) == 1:
            return possible_moves[0]
        for move in possible_moves:
            if move.command == MoveEnum.END_TURN:
                possible_moves.remove(move)
        pick = random.choice(possible_moves)
        return pick
    
    def game_end(self, end_game_state, final_state):
        pass