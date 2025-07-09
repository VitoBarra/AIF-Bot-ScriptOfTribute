import re
import numpy as np

from scripts_of_tribute.board import GameState
from scripts_of_tribute.enums import PlayerEnum


def utilityFunction_PrestigeAndPower( game_state):
    return game_state.current_player.prestige + game_state.current_player.power


def HandStatistics(game_state: GameState, regex):
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

def CalculateMaxMinAverageCoin(game_state: GameState):
    return HandStatistics(game_state,"GAIN_COIN")

def CalculateMaxMinAveragePowerAndPrestige( game_state: GameState):
    return HandStatistics(game_state, "GAIN_POWER|GAIN_PRESTIGE")

def CalculateFavor(game_state:GameState, player_id):
    patron_favor = game_state.patron_states.patrons.items()
    favor = 0
    for patron_id, player_enum in patron_favor:
        if player_enum == PlayerEnum.NO_PLAYER_SELECTED:
            continue # if the patron favor is neutral, ignore it
        elif player_enum == player_id:
            favor = favor + 1
        else:
            favor = favor - 1
    return favor

def CalculateCoinLeft(game_state: GameState):
    return game_state.current_player.coins

def utilityFunction_MIXMAXAVERAGERES(game_state: GameState) ->float:
        top_hand_coin,bottom_hand_coin, average_Hand_coin, average_singleCard_coin = CalculateMaxMinAverageCoin(game_state)
        top_hand_PEP,bottom_hand_PEP, average_Hand_PEP, average_singleCard_PEP = CalculateMaxMinAveragePowerAndPrestige(game_state)
        favor = CalculateFavor(game_state, game_state.current_player.player_id)
        coin_left = CalculateCoinLeft(game_state)
        prestige  = game_state.current_player.prestige
        power     = game_state.current_player.power


        param   = np.array([np.log(top_hand_coin),bottom_hand_coin, average_Hand_coin, average_singleCard_coin,
                            top_hand_PEP**1.3,bottom_hand_PEP, average_Hand_PEP, average_singleCard_PEP,
                            prestige, power,
                            np.sign(favor) * favor**2, -coin_left, -game_state.enemy_player.prestige**1.1])
        weight  = np.ones((1,param.shape[0])) # trained
        utility = weight @ param
        return float(utility[0])