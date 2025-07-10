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