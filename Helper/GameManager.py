from scripts_of_tribute.game import Game
from Helper.HidePrint import HiddenPrints

## This file is needed primarily to avoid circular imports


def RunGames(bot_1, name_1, bot_2 ,name_2,runs=30, threads=5, hide_print=False):

    if hide_print:
        HiddenPrints.HidePrint()

    game = Game()
    game.register_bot(bot_1)
    game.register_bot(bot_2)

    game.run(
        name_1,
        name_2,
        start_game_runner=True,
        runs=runs ,
        threads=threads
    )

    if hide_print:
        HiddenPrints.ResumePrint()