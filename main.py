from scripts_of_tribute.game import Game
from MaxPrestigeSettableDepthBot import MaxPrestigeSettableDepthBot
from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot


if __name__ == "__main__":
    depth = 3
    bot1_name="MAX_Prestige_2_Moves"
    bot2_name=f"recursive_MAX_Prestige_{depth}_Moves"
    bot1 = MaxPrestigeBot(bot_name=bot1_name)
    bot2 = MaxPrestigeSettableDepthBot(bot_name=bot2_name,depth=depth)

    # bot2_name = f"MAX_Prestige_2_Moves_1"
    # bot1_name = f"MAX_Prestige_2_Moves_2"
    # bot1 = MaxPrestigeBot(bot_name=bot1_name)
    # bot2 = MaxPrestigeBot(bot_name=bot2_name)


    game = Game()
    game.register_bot(bot1)
    game.register_bot(bot2)

    game.run(
        bot1_name,
        bot2_name,
        start_game_runner=True,
        runs=10,
        threads=2,
    )