from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot
from Helper.GameManager import RunGames
from HeuristicLerning.EvolutionaryHeuristic import evolutionary_algorithm, Individual
from Helper.LoggerFilesHelper import CleanUpLogs
from bots.AIFBot_MCTS import AIFBotMCTS
from bots.BoundedDS import BoundedDS

from BotCommon.Heuristics import WeightedUtilityFunction_MMHVR, WeightedUtilityFunction_MMHVR_plain
from BotCommon.Heuristics import utilityFunction_PrestigeAndPower

#=====Settings=====
HIDE_PRINT = False
RUN_NUM = 30
THREAD_NUM = 5


def Evolve():
    ind = evolutionary_algorithm(20,  200, 2, 5, 10, 13,True)
    ind.save("individual",1)
def load_individual():
    ind = Individual.load("individual",1)
    return ind

def MakeRun():
    depth = 2

    maxPrestige_name           = f"MAX_Prestige_{depth}_Moves"
    BoundedDS_WMMHVR_name       = f"BoundedDS_WMMHVR_{depth}_Moves"
    aif_MMHVR_name             = f"AIFBOT_MMHVR_{depth}_Moves"
    aif_MCTS_WMMHVR_name       = f"AIFBOT_MCTS_WMMHVR"
    aif_MCTS_WMMHVR_evolved_name = f"AIFBOT_MCTS_WMMHVR_evolved"
    aif_MCTS_Max_Prestige_name = f"AIFBOT_MCTS_Max_Prestige"
    random_name                = f"RandomBot"

    bot_maxPrestige            = MaxPrestigeBot               (bot_name=maxPrestige_name)
    bot_BoundedDS_WMMHVR     = BoundedDS                      (bot_name=BoundedDS_WMMHVR_name, depth=depth,
                                                               evaluation_function=WeightedUtilityFunction_MMHVR)
    bot_aif_MCTS_WMMHVR        = AIFBotMCTS                   (bot_name=aif_MCTS_WMMHVR_name,
                                                               evaluation_function= WeightedUtilityFunction_MMHVR)
    bot_aif_MCTS_Max_Prestige  = AIFBotMCTS                   (bot_name=aif_MCTS_Max_Prestige_name,
                                                               evaluation_function= utilityFunction_PrestigeAndPower)
    bot_random                 = RandomBot                    (bot_name=random_name)

    ind = load_individual()
    bot_aif_MCTS_WMMHVR_evolved = AIFBotMCTS(aif_MCTS_WMMHVR_evolved_name, WeightedUtilityFunction_MMHVR_plain,
                                             None, ind.weights, ind.activations)


    RunGames(bot_aif_MCTS_WMMHVR, bot_aif_MCTS_WMMHVR_evolved, runs=RUN_NUM, threads=THREAD_NUM, hide_print=HIDE_PRINT)


if __name__ == "__main__":
    # results_from_log()
    CleanUpLogs()
    # MakeRun()
    Evolve()