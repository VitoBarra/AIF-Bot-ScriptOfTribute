from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot
from Helper.GameManager import RunGames
from HeuristicLerning.EvolutionaryHeuristic import evolutionary_algorithm
from Helper.LoggerFilesHelper import CleanUpLogs
from bots.AIFBot_MMHVR import AIFBot_MMHVR
from bots.AIFBot_MCTS import AIFBotMCTS


#=====Settings=====
HIDE_PRINT = True
RUN_NUM = 30
THREAD_NUM = 5



def MakeRun():
    depth = 2
    maxPrestige_name     = f"MAX_Prestige_2_Moves"
    aif_MMHVR_name       = f"AIFBOT_MMHVR_{depth}_Moves"
    aif_MCTS_name        = f"AIFBOT_MCTS"
    random_name          = f"RandomBot"

    bot_maxPrestige      = MaxPrestigeBot  (bot_name=maxPrestige_name)
    bot_MMHVR_aif        = AIFBot_MMHVR    (bot_name=aif_MMHVR_name, depth=depth)
    bot_aif_MCTS         = AIFBotMCTS      (bot_name=aif_MCTS_name)
    bot_random           = RandomBot       (bot_name=random_name)


    RunGames(bot_aif_MCTS, aif_MCTS_name, bot_maxPrestige, maxPrestige_name,
             runs=RUN_NUM, threads=THREAD_NUM, hide_print=HIDE_PRINT)



if __name__ == "__main__":
    # results_from_log()
    CleanUpLogs()
    MakeRun()