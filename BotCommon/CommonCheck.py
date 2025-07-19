import random

import numpy as np
from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove, SimpleCardMove, MakeChoiceMoveUniqueCard, MakeChoiceMoveUniqueEffect


def CheckForGoalState(game_state, player_id) -> bool:
    return game_state.end_game_state is not None and game_state.end_game_state.winner == player_id


def NewPossibleMoveAvailable(moves:list[BasicMove]) -> bool:
    return not (len(moves) == 1 and moves[0].command == MoveEnum.END_TURN)



def MatchCommand(move: BasicMove, move_list: list[BasicMove]):
    possible_moves = [m for m in move_list if m.command == move.command]

    if  len(possible_moves) <=1:
        print("No moves available")
        return next(m for m in move_list if m.command == MoveEnum.END_TURN)

    match move.command:
        case MoveEnum.PLAY_CARD | MoveEnum.BUY_CARD:
            return next(m for m in possible_moves if m.cardUniqueId == move.cardUniqueId)
        case MoveEnum.CALL_PATRON | MoveEnum.ACTIVATE_AGENT | MoveEnum.ATTACK:
            return next(m for m in possible_moves if m.patronId == move.patronId)
        case MoveEnum.MAKE_CHOICE:
            return next(m for m in possible_moves if m.cardsUniqueIds == move.cardsUniqueIds)
        case MoveEnum.END_TURN | _:
            return next(m for m in move_list if m.command == MoveEnum.END_TURN)

def IsPriorMoves(move: BasicMove, game_state: GameState) -> bool:
    if isinstance(move, SimpleCardMove) and move.command != MoveEnum.BUY_CARD:
        return True
    elif isinstance(move, MakeChoiceMoveUniqueEffect) and move.command == MoveEnum.MAKE_CHOICE:

        return True
    else:
        #print(f"Command: {move.command}, Type: {type(move).__name__}")
        return False


def depth_sample(game_state: GameState, possible_moves:list[BasicMove]) -> tuple[int, list[float]]:
    current_game_state = game_state
    current_possible_moves = possible_moves
    sample_branching_factors= []

    while len(current_possible_moves)>1:
        sample_branching_factors.append(len(current_possible_moves))
        current_possible_moves = [move for move in current_possible_moves if move.command != MoveEnum.END_TURN]
        current_possible_move = random.choice(current_possible_moves)
        current_game_state, current_possible_moves = current_game_state.apply_move(current_possible_move)


    return len(sample_branching_factors), sample_branching_factors

def estimate_depth(game_state: GameState, possible_moves:list[BasicMove]) -> tuple[int, list[float]]:
    max_sample_depth = 0
    bs = []
    for i in range(5):
        sample_depth, sample_branching_factors = depth_sample(game_state, possible_moves)
        bs.append(sample_branching_factors)
        if sample_depth > max_sample_depth:
            max_sample_depth = sample_depth

    # mediate on branching factors
    bs = [np.array(x) for x in bs]
    max_len = max(len(x) for x in bs)
    bs_padded = np.array([np.pad(x, (0, max_len - len(x))) for x in bs])
    bs_masked = np.where(bs_padded == 0, np.nan, bs_padded)
    bf_mean = np.nanmean(bs_masked, axis=0).astype(float).tolist()

    return max_sample_depth, bf_mean
