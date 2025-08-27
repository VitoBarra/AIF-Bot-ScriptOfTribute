from BotCommon.Heuristics import utilityFunction_PrestigeAndPower, utilityFunction_MMHVR, \
    WeightedUtilityFunction_MMHVR_plain
from ExampleBot.RandomBot import RandomBot
from Helper.GameManager import TryAsFirstAndSecondPlayer_PrintReasonFromLog
from HeuristicLearning.EvolutionaryHeuristic import evolutionary_algorithm, Individual
from Helper.LoggerFilesHelper import CleanUpLogs, results_from_log, PrintWinningReasonFromLog
from bots.AIFBot_MCTS import AIFBotMCTS
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
    depth = 2

    BoundedDS_WMMHVR_name       = f"BoundedDS_WMMHVR_{depth}_Moves"
    aif_MMHVR_name             = f"AIFBOT_MMHVR_{depth}_Moves"
    aif_MCTS_WMMHVR_name       = f"AIFBOT_MCTS_WMMHVR"
    aif_MCTS_maxPrestige_name  = f"AIFBOT_MCTS_MAXPRESTIGE"
    aif_MCTS_WMMHVR_evolved_name = f"AIFBOT_MCTS_WMMHVR_evolved"
    random_name                = f"RandomBot"

    bot_BoundedDS_WMMHVR       = BoundedDS                    (bot_name=BoundedDS_WMMHVR_name, depth=depth,
                                                               evaluation_function= utilityFunction_MMHVR)
    bot_aif_MCTS_WMMHVR        = AIFBotMCTS                   (bot_name=aif_MCTS_WMMHVR_name,
                                                               evaluation_function= utilityFunction_MMHVR)
    bot_aif_MCTS_Max_Prestige  = AIFBotMCTS                   (bot_name=aif_MCTS_maxPrestige_name,
                                                               evaluation_function= utilityFunction_PrestigeAndPower)
    bot_random                 = RandomBot                    (bot_name=random_name)

    ind = Individual.LoadLatest("gen")
    bot_aif_MCTS_WMMHVR_evolved = AIFBotMCTS                  (bot_name=aif_MCTS_WMMHVR_evolved_name,
                                                                evaluation_function=WeightedUtilityFunction_MMHVR_plain,
                                                               weights= ind.weights, functions=ind.activations)

    TryAsFirstAndSecondPlayer_PrintReasonFromLog(bot_aif_MCTS_WMMHVR, bot_BoundedDS_WMMHVR, runs=RUN_NUM, threads=THREAD_NUM, hide_print=HIDE_PRINT)

if __name__ == "__main__":
    # results_from_log()
    MakeRun()
    # Evolve()
    # plot_convergence_from_checkpoints(20,13)
    # plotSingleWeight_from_checkpoints(20,13)
