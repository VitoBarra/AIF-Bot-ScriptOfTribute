from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import PatronId
from scripts_of_tribute.move import BasicMove


class AIFBot(BaseAI):


    def pregame_prepare(self):
        """Optional: Prepare your bot before the game starts."""
        pass


    def select_patron(self, available_patrons: list[PatronId]) -> PatronId:
        """Choose a patron from the available list."""
        raise NotImplementedError


    def play(self, game_state: GameState, possible_moves: list[BasicMove], remaining_time: int) -> BasicMove:
        """Choose a move based on the current game state."""
        raise NotImplementedError


    def game_end(self, final_state):
        """Optional: Handle end-of-game logic."""
        pass