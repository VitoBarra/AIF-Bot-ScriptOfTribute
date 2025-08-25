from BotCommon.Heuristics import utilityFunction_PrestigeAndPower, utilityFunction_MMHVR, \
    WeightedUtilityFunction_MMHVR_plain
from ExampleBot.RandomBot import RandomBot
from Helper.GameManager import TryAsFirstAndSecondPlayer_PrintReasonFromLog
from HeuristicLearning.EvolutionaryHeuristic import evolutionary_algorithm, Individual
from Helper.LoggerFilesHelper import CleanUpLogs, results_from_log, PrintWinningReasonFromLog
from bots.AIFBot_MCTS import AIFBotMCTS, MCTSenum
from bots.BoundedDS import BoundedDS
from HeuristicLearning.EvoPlot import plot_convergence_from_checkpoints, plotSingleWeight_from_checkpoints

#=====Settings=====
HIDE_PRINT = True
RUN_NUM = 30
THREAD_NUM = 5


def Evolve():
    ind = evolutionary_algorithm(20,  200, 2, 5, 10, 13,True)
    ind.save("individual",1)



def MakeRun():
    bot_BoundedDS_WMMHVR   = BoundedDS                    (bot_name="BoundedDS_WMMHVR_2_Moves", depth=2, use_prior_move= False,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_MCTS2_WMMHVR       = AIFBotMCTS                   (bot_name="MCTS2_WMMHVR",       MCTSversion= MCTSenum.MCTS2,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_FlatMCTS_WMMHVR    = AIFBotMCTS                   (bot_name="flatMCTS_WMMHVR",    MCTSversion= MCTSenum.FlatMCTS,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_MCTS_WMMHVR        = AIFBotMCTS                   (bot_name="MCTS_WMMHVR",        MCTSversion= MCTSenum.MCTS,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_ProgMCTS_WMMHVR    = AIFBotMCTS                   (bot_name="ProgMCTS_WMMHVR",    MCTSversion= MCTSenum.ProgressiveMCTS,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_DMultyTMCTS_WMMHVR = AIFBotMCTS                   (bot_name="DMultyMCTS_WMMHVR",  MCTSversion= MCTSenum.DMultyTMCTS,
                                                           evaluation_function= utilityFunction_MMHVR)
    bot_DSingleTMCTS_WMMHVR= AIFBotMCTS                   (bot_name="DSingleMCTS_WMMHVR", MCTSversion= MCTSenum.DSingleTMCTS,
                                                           evaluation_function=utilityFunction_MMHVR)
    bot_MCTS2_Max_Prestige = AIFBotMCTS                   (bot_name="MCTS2_MAX_prestige", MCTSversion= MCTSenum.MCTS2,
                                                           evaluation_function= utilityFunction_PrestigeAndPower)
    bot_random             = RandomBot                    (bot_name="RandomBot")

    ind = Individual.LoadLatest("gen")
    bot_MCTS_WMMHVR_evolved = AIFBotMCTS                  (bot_name="MCTS2_WMMHVR_evolved", MCTSversion= MCTSenum.MCTS2,
                                                           evaluation_function=WeightedUtilityFunction_MMHVR_plain,
                                                           weights=ind.weights, functions=ind.activations)

    TryAsFirstAndSecondPlayer_PrintReasonFromLog(bot_DMultyTMCTS_WMMHVR, bot_BoundedDS_WMMHVR, runs=RUN_NUM, threads=THREAD_NUM, hide_print=HIDE_PRINT)

if __name__ == "__main__":
    # results_from_log()
    MakeRun()
    # Evolve()
    # plot_convergence_from_checkpoints(20,13)
    # plotSingleWeight_from_checkpoints(20,13)
