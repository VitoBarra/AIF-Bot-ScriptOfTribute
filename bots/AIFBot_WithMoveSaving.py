import os
import random
import re

import numpy as np

from scripts_of_tribute.base_ai import BaseAI
from scripts_of_tribute.board import GameState, EndGameState
from scripts_of_tribute.enums import PatronId, MoveEnum, PlayerEnum
from scripts_of_tribute.move import BasicMove, SimpleCardMove, SimplePatronMove


class AIFBotMoveSaving(BaseAI):

    ## ========================SET UP========================
    def __init__(self, bot_name,depth, seed=None):
        super().__init__(bot_name)
        self.player_id: PlayerEnum = PlayerEnum.NO_PLAYER_SELECTED
        self.start_of_game: bool = True
        self.depth: int = depth
        self.best_moves:list[BasicMove] = []
        self.seed = seed if seed is not None else random.randint(0, 2**64)

    def select_patron(self, available_patrons):
        pick = random.choice(available_patrons)
        return pick

    ## ========================Heuristic========================
    def HandStatistics(self, game_state: GameState, regex):
        cards = game_state.current_player.draw_pile + game_state.current_player.hand + game_state.current_player.cooldown_pile
        pattern = re.compile(rf"({regex}) (\d+)")

        valid_card = [
            (card, int(pattern.match(effect).group(2)))
            for card in cards
            for effect in card.effects
            if pattern.match(effect)
        ]
        if valid_card is [] or valid_card is None:
            print("no valid card founded")
            return 0,0,0,0

        cards_sorted = sorted(valid_card, key=lambda x: x[1], reverse=True)

        top_5_hand = sum(n for _, n in cards_sorted[:5])
        bottom_5_hand = sum(n for _, n in cards_sorted[-5:])
        average_singleCard = sum(n for _, n in cards_sorted) / len(cards_sorted) if cards_sorted else 0
        average_Hand = (top_5_hand + bottom_5_hand)/ 2

        return top_5_hand,bottom_5_hand, average_Hand,average_singleCard

    def CalculateMaxMinAverageCoin(self,game_state: GameState):
        return self.HandStatistics(game_state,"GAIN_COIN")

    def CalculateMaxMinAveragePowerAndPrestige(self, game_state: GameState):
        return self.HandStatistics(game_state, "GAIN_POWER|GAIN_PRESTIGE")

    def CalculateFavor(self,game_state:GameState):
        patron_favor = game_state.patron_states.patrons.items()
        favor = 0
        for patron_id, player_enum in patron_favor:
            if player_enum == PlayerEnum.NO_PLAYER_SELECTED:
                continue # if the patron favor is neutral, ignore it
            elif player_enum == self.player_id:
                favor = favor + 1
            else:
                favor = favor - 1
        return favor

    def CalculateCoinLeft(self,game_state: GameState):
        return game_state.current_player.coins

    def utilityFunction(self, game_state)->float:
            top_hand_coin,bottom_hand_coin, average_Hand_coin, average_singleCard_coin = self.CalculateMaxMinAverageCoin(game_state)
            top_hand_PEP,bottom_hand_PEP, average_Hand_PEP, average_singleCard_PEP = self.CalculateMaxMinAveragePowerAndPrestige(game_state)
            favor = self.CalculateFavor(game_state)
            coin_left = self.CalculateCoinLeft(game_state)

            param   = np.array([np.log(top_hand_coin),bottom_hand_coin, average_Hand_coin, average_singleCard_coin,
                                top_hand_PEP**1.3,bottom_hand_PEP, average_Hand_PEP, average_singleCard_PEP,
                                game_state.current_player.prestige, game_state.current_player.power,
                                np.sign(favor) * favor**2, -coin_left])
            weight  = np.ones((1,param.shape[0])) # trained
            utility = weight @ param
            return float(utility[0])

    ## ========================Functionality========================
    def CheckForGoalState(self, game_state) -> bool:
        if game_state.end_game_state is not None:
            # Check if the game is over, if we win, we are fine with this move
            if game_state.end_game_state.winner == self.player_id:
                return True
        return False

    def NewPossibleMoveAviable(self, moves):
        return not (len(moves) == 1 and moves[0].command == MoveEnum.END_TURN)

    def ExploreMoveAvailable(self, possible_moves:list[BasicMove], game_state:GameState) ->list[BasicMove]:
        if not self.NewPossibleMoveAviable(possible_moves):
            # If there are no moves possible, select the end of turn move
            return [next(move for move in possible_moves if move.command == MoveEnum.END_TURN)]

        best_moves = None
        best_moves_val = float("-inf")
        for evaluating_move in possible_moves:
            if evaluating_move.command == MoveEnum.END_TURN:
                # Skip the END_TURN command
                continue

            curr_val, moves = self.EvaluateMove(evaluating_move,game_state,self.depth-1)
            if curr_val == float('inf'):
                # Goal State found, can return early
                return moves
            elif best_moves_val < curr_val:
               best_moves_val = curr_val
               best_moves = moves

        return best_moves if best_moves is not None else []

    def EvaluateMove(self,move, game_state, depth:int)->(float, list[BasicMove]):
        # Move Evaluation (Depth first approach)
        local_game_state, new_moves = game_state.apply_move(move,self.seed)

        if self.CheckForGoalState(local_game_state):
            return float('inf'), [move]

        if depth == 0 or not self.NewPossibleMoveAviable(new_moves):
            return self.utilityFunction(local_game_state), [move]

        move_value=[]
        for new_move in new_moves:
            if new_move.command == MoveEnum.END_TURN:
                continue
            move_value.append(self.EvaluateMove(new_move, local_game_state, depth-1))

        max_value, list_of_move = max(move_value, key=lambda x: x[0], default=(0, []))

        if len (list_of_move)==0:
            print ("legal move list is empty")

        return max_value , [move] + list_of_move

    def play(self, game_state: GameState, possible_moves:list[BasicMove], remaining_time: int) -> BasicMove:
        # Set Up
        if self.start_of_game:
            self.player_id = game_state.current_player.player_id
            self.start_of_game = False

        if len(self.best_moves)<=0:
            # Move Evaluation
            self.best_moves = self.ExploreMoveAvailable(possible_moves, game_state)

        best_move:BasicMove = self.MatchCommand(self.best_moves.pop(), possible_moves)


        if best_move in possible_moves:
            print(f"played:  {best_move.command}: {best_move.move_id}")
            if best_move.command == MoveEnum.BUY_CARD:
                # Recalculate the best move after a non-deterministic move
                self.best_moves = []
            return best_move
        elif best_move is None:
            print("unexpected game state, returning end of turn")
            return next(move for move in possible_moves if move.command == MoveEnum.END_TURN)
        else:
            print(f"tried to do an illegal move {best_move.command}: {best_move.move_id}")
            return next(move for move in possible_moves if move.command == MoveEnum.END_TURN)

    def MatchCommand(self,move:BasicMove, move_list:list[BasicMove]):
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


    def game_end(self, end_game_state: EndGameState, final_state: GameState):
        # Example how you can log your game for further analysis
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        filename = f"game_log_{final_state.state_id}_{end_game_state.winner}.log"
        filepath = os.path.join(log_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"=== Game Ended ===\n")
                f.write(f"Winner: {end_game_state.winner}\n")
                f.write(f"Reason: {end_game_state.reason}\n")
                f.write(f"Context: {end_game_state.AdditionalContext}\n\n")
                f.write("=== Completed Actions ===\n")

                for action in final_state.completed_actions:
                    f.write(action + "\n")

            print(f"[INFO] Game log saved to: {filepath}")

        except Exception as e:
            print(f"[ERROR] Failed to save game log: {e}")