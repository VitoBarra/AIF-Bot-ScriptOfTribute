from scripts_of_tribute.game import Game
from Helper.HidePrint import HiddenPrints
from Helper.LoggerFilesHelper import CleanUpLogs, PrintWinningReasonFromLog


## This file is needed primarily to avoid circular imports


def RunGames(bot_1, bot_2, runs=30, threads=5, timeOutS :int = 10, hide_print=False, base_client_port=50000, base_server_port=49000):

    if hide_print:
        HiddenPrints.HidePrint()

    print(f"PLAYER 1: {bot_1.bot_name} | PLAYER 2 : {bot_2.bot_name}")
    game = Game()
    game.register_bot(bot_1)
    game.register_bot(bot_2)

    game.run(
        bot_1.bot_name,
        bot_2.bot_name,
        start_game_runner=True,
        runs=runs ,
        threads=threads,
        timeout=timeOutS,
        base_client_port= base_client_port,
        base_server_port= base_server_port,
    )

    if hide_print:
        HiddenPrints.ResumePrint()




def TryAsFirstAndSecondPlayer_PrintReasonFromLog(bot_1, bot_2, runs=30, threads=5, timeOutS :int = 10, hide_print=False, base_client_port=50000, base_server_port=49000):
    CleanUpLogs()
    RunGames(bot_1, bot_2, runs=runs, threads=threads, timeOutS=timeOutS, hide_print=hide_print, base_client_port=base_client_port, base_server_port=base_server_port)
    PrintWinningReasonFromLog()

    CleanUpLogs()
    RunGames(bot_2, bot_1, runs=runs, threads=threads, timeOutS=timeOutS, hide_print=hide_print, base_client_port=base_client_port, base_server_port=base_server_port)
    PrintWinningReasonFromLog()



def TryAsFirstAndSecondPlayer(bot_1, bot_2, runs=30, threads=5, timeOutS :int = 10, hide_print=False, base_client_port=50000, base_server_port=49000):
    RunGames(bot_1, bot_2, runs=runs, threads=threads, timeOutS=timeOutS, hide_print=hide_print, base_client_port=base_client_port, base_server_port=base_server_port)
    RunGames(bot_2, bot_1, runs=runs, threads=threads, timeOutS=timeOutS, hide_print=hide_print, base_client_port=base_client_port, base_server_port=base_server_port)
