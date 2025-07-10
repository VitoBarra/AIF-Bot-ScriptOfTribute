from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import MoveEnum
from scripts_of_tribute.move import BasicMove, SimpleCardMove, MakeChoiceMoveUniqueCard, MakeChoiceMoveUniqueEffect


def CheckForGoalState(game_state, player_id) -> bool:
    return game_state.end_game_state is not None and game_state.end_game_state.winner == player_id


def NewPossibleMoveAvailable(moves:list[BasicMove]) -> bool:
    return not (len(moves) == 1 and moves[0].command == MoveEnum.END_TURN)


def MatchCommand(move:BasicMove, move_list:list[BasicMove]):
    possible_moves = [move_filter for move_filter in move_list if move_filter.command == move.command]

    if len(possible_moves) ==0:
        print("No moves available")
        return next(move for move in move_list if move.command == MoveEnum.END_TURN)

    if move.command == MoveEnum.PLAY_CARD:
        return next(best_move for best_move in possible_moves if best_move.cardUniqueId==move.cardUniqueId)
    elif move.command == MoveEnum.CALL_PATRON:
        return next(best_move for best_move in possible_moves if best_move.patronId==move.patronId)
    elif move.command == MoveEnum.ACTIVATE_AGENT:
        return next(best_move for best_move in possible_moves if best_move.patronId==move.patronId)
    elif move.command == MoveEnum.ATTACK:
        return next(best_move for best_move in possible_moves if best_move.patronId==move.patronId)
    elif move.command == MoveEnum.BUY_CARD:
        return next(best_move for best_move in possible_moves if best_move.cardUniqueId==move.cardUniqueId)
    elif move.command == MoveEnum.MAKE_CHOICE:
         return next (best_move for best_move in possible_moves if best_move.cardsUniqueIds==move.cardsUniqueIds)
    else: # MoveEnum.END_TURN or null
        return next(move for move in move_list if move.command == MoveEnum.END_TURN)

def IsPriorMoves(move: BasicMove, game_state: GameState) -> bool:
    if isinstance(move, SimpleCardMove) and move.command != MoveEnum.BUY_CARD:
        return True
    elif isinstance(move, MakeChoiceMoveUniqueEffect) and move.command == MoveEnum.MAKE_CHOICE:

        return True
    else:
        #print(f"Command: {move.command}, Type: {type(move).__name__}")
        return False