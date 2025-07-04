import random

from scripts_of_tribute.base_ai import BaseAI

class RandomBot(BaseAI):
    
    def select_patron(self, available_patrons):
        return random.choice(available_patrons)
    
    def play(self, game_state, possible_moves, remaining_time):
        pick = random.choice(possible_moves)
        return pick
    
    def game_end(self, end_game_state, final_state):
        pass