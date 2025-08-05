import numpy as np
from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove


def calculate_ucb(total_utility:float, number_of_visit:int, parents_number_of_visit:int, c:float = np.sqrt(2)) -> float:
    if number_of_visit == 0 or parents_number_of_visit == 0:
        return float('inf') # If no playouts, return infinity to encourage exploration on never seen nodes

    exploitation_term = total_utility / number_of_visit
    exploration_term = np.log(parents_number_of_visit) / number_of_visit

    return exploitation_term + c * np.sqrt(exploration_term)


def deterministic_test(game_state: GameState, parent_move: BasicMove):
    pgs = game_state
    sgs1, ps1 = pgs.apply_move(parent_move)
    sgs1.initial_seed = 48

    for pick in ps1:
        sgs2, ps2 = sgs1.apply_move(pick)
        sgs21, ps21 = sgs1.apply_move(pick)
        for tavern_card2 in sgs2.tavern_available_cards:
            for tavern_card21 in sgs21.tavern_available_cards:
                if tavern_card2.name != tavern_card21.name:
                    pass
        if len(ps2) != len(ps21):
            pass