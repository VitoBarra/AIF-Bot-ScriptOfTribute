from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove


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