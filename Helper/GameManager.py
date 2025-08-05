from scripts_of_tribute.game import Game
from Helper.HidePrint import HiddenPrints

## This file is needed primarily to avoid circular imports


def RunGames(bot_1, bot_2,runs=30, threads=5, hide_print=False):

    if hide_print:
        HiddenPrints.HidePrint()

    game = Game()
    game.register_bot(bot_1)
    game.register_bot(bot_2)

    game.run(
        bot_1.bot_name,
        bot_2.bot_name,
        start_game_runner=True,
        runs=runs ,
        threads=threads
    )

    if hide_print:
        HiddenPrints.ResumePrint()