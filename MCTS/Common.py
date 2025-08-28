import time

import numpy as np
import random
from scripts_of_tribute.board import GameState
from scripts_of_tribute.move import BasicMove
from scripts_of_tribute.enums import MoveEnum
from BotCommon.CommonCheck import CheckForGoalState


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

def playout(move: BasicMove, game_state: GameState, player_id, b = None) -> GameState:
    while not (CheckForGoalState(game_state, player_id) or move.command == MoveEnum.END_TURN):
        try:
            game_state, possible_moves = game_state.apply_move(move)
        except Exception as e:
            print(e)
            raise ValueError ("problems with apply_move")
        if len(possible_moves) == 1:
            move = possible_moves[0]
            continue
        if b is not None:
            b.append(len(possible_moves)-1)

        move = random.choice([m for m in possible_moves if m.command != MoveEnum.END_TURN])
    return game_state


def calculate_time_to_give(b: list[int], remaining_time: int) -> int:
    n = len(b)
    if n < 1:
        raise ValueError("b must have at least one element in calculate_time_to_give")

    factor = 1
    total_factor = 1
    for i in range(n - 1):
        factor /= b[i]
        total_factor += factor

    return int(remaining_time / total_factor)

def give_time(game_state: GameState, possible_moves:list[BasicMove], remaining_time: int, player_id) -> int:
    start = time.perf_counter()
    if len(possible_moves) <= 1:
        raise ValueError("b must have at least two elements in give_time")

    time_to_give = []
    for move in possible_moves:
        if move.command == MoveEnum.END_TURN:
            continue
        b: list[int] = [len(possible_moves)-1] # minus 1 for the end-of-turn move
        playout(move, game_state, player_id, b)
        t_0 = calculate_time_to_give(b, remaining_time)
        time_to_give.append(t_0)

    execution_time_ms = (time.perf_counter() - start) * 1000
    if len(time_to_give) == 0:
        raise ValueError("No valid moves found to allocate time to.")

    return min(time_to_give) - int(execution_time_ms)