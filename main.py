from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot
from Helper.GameManager import RunGames
from HeuristicLerning.EvolutionaryHeuristic import evolutionary_algorithm
from Helper.LoggerFilesHelper import CleanUpLogs
from bots.AIFBot_MMHVR import AIFBot_MMHVR
from bots.AIFBot_MCTS import AIFBotMCTS
from bots.BoundedDS import BoundedDS

from BotCommon.Heuristics import WeightedUtilityFunction_MMHVR
from BotCommon.Heuristics import utilityFunction_PrestigeAndPower

#=====Settings=====
HIDE_PRINT = True
RUN_NUM = 30
THREAD_NUM = 5


def Evolve():
    ind = evolutionary_algorithm(20,  200, 2, 5, 10, 13,True)
    ind.save("individual",1)

def MakeRun():
    depth = 2

    maxPrestige_name           = f"MAX_Prestige_{depth}_Moves"
    BoundedDS_WMMHVR_name       = f"BoundedDS_WMMHVR_{depth}_Moves"
    aif_MMHVR_name             = f"AIFBOT_MMHVR_{depth}_Moves"
    aif_MCTS_WMMHVR_name       = f"AIFBOT_MCTS_WMMHVR"
    aif_MCTS_Max_Prestige_name = f"AIFBOT_MCTS_Max_Prestige"
    random_name                = f"RandomBot"

    bot_maxPrestige            = MaxPrestigeBot               (bot_name=maxPrestige_name)
    bot_BoundedDS_WMMHVR     = BoundedDS                      (bot_name=BoundedDS_WMMHVR_name, depth=depth,
                                                               evaluation_function=WeightedUtilityFunction_MMHVR)
    bot_MMHVR_aif              = AIFBot_MMHVR                 (bot_name=aif_MMHVR_name, depth=depth)
    bot_aif_MCTS_WMMHVR        = AIFBotMCTS                   (bot_name=aif_MCTS_WMMHVR_name,
                                                               evaluation_function= WeightedUtilityFunction_MMHVR)
    bot_aif_MCTS_Max_Prestige  = AIFBotMCTS                   (bot_name=aif_MCTS_Max_Prestige_name,
                                                               evaluation_function= utilityFunction_PrestigeAndPower)
    bot_random                 = RandomBot                    (bot_name=random_name)

    RunGames(bot_aif_MCTS_WMMHVR, bot_BoundedDS_WMMHVR, runs=RUN_NUM, threads=THREAD_NUM, hide_print=HIDE_PRINT)


if __name__ == "__main__":
    # results_from_log()
    CleanUpLogs()
    # MakeRun()
    Evolve()