from scripts_of_tribute.game import Game

from AIFBot import AIFBot
from MaxPrestigeSettableDepthBot import MaxPrestigeSettableDepthBot
from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot


if __name__ == "__main__":
    depth = 2
    maxPrestige_name = f"MAX_Prestige_2_Moves"
    aif_name         = f"AIFBOT_Moves_{depth}"
    random_name      = f"RandomBot"

    bot_maxPrestige  = MaxPrestigeBot (bot_name=maxPrestige_name)
    bot_aif          = AIFBot         (bot_name=aif_name,depth=depth)
    bot_random       = RandomBot      (bot_name=random_name)


    game = Game()
    game.register_bot(bot_aif)
    game.register_bot(bot_maxPrestige)

    game.run(
        maxPrestige_name,
        aif_name,
        start_game_runner=True,
        runs=14,
        threads=2,
    )