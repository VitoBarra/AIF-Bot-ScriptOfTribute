import random
from operator import contains

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import PatronId
from scripts_of_tribute.move import BasicMove


class AIFBot(BaseAI):

    call = 0

    def pregame_prepare(self):
        """Optional: Prepare your bot before the game starts."""


    def select_patron(self, available_patrons: list[PatronId]) -> PatronId:
        """Choose a patron from the available list."""
        print(f"called {self.call} times with of {len(available_patrons)} patrons")
        for a in available_patrons:
            print(f"Patron: {a}")

        if PatronId.TREASURY in available_patrons:
            print(f"selected TRESURE at time {self.call}")
            pick = PatronId.TREASURY

        elif PatronId.PELIN in available_patrons:
            print(f"selected PELIN at time {self.call}")
            pick = PatronId.PELIN
        elif PatronId.HLAALU in available_patrons:
            print(f"selected HLAALU at time {self.call}")
            pick = PatronId.HLAALU
        else:
            print(f"selected random at time {self.call}")
            pick = random.choice(available_patrons)
        self.call= self.call+1
        return pick


    def play(self, game_state: GameState, possible_moves: list[BasicMove], remaining_time: int) -> BasicMove:
        """Choose a move based on the current game state."""
        pick = random.choice(possible_moves)
        return pick


    def game_end(self, final_state):
        """Optional: Handle end-of-game logic."""
        pass