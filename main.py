import os
import shutil
from collections import Counter

from scripts_of_tribute.game import Game


from ExampleBot.MaxPrestigeBot import MaxPrestigeBot
from ExampleBot.RandomBot import RandomBot
from bots.AIFBot_MMHVR import AIFBot_MMHVR
from bots.AIFBot_MCTS import AIFBotMCTS


#=====Settings=====
LOG_FOLDER_NAME = "logs"


RUN_NUM = 30
THREAD_NUM = 5

def results_from_log():
    # Counter for winners
    winner_counts = Counter()
    total_files = 0

    # Loop through each file in the folder
    for filename in os.listdir(LOG_FOLDER_NAME):
        file_path = os.path.join(LOG_FOLDER_NAME, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                for line in file:
                    if line.startswith("Winner:"):
                        winner = line.strip().split(":")[1].strip()
                        winner_counts[winner] += 1
                        total_files += 1
                        break  # Stop after finding the Winner line

    # Display the results
    print("Winner Stats:")
    for winner, count in winner_counts.items():
        percentage = (count / total_files) * 100
        print(f"{winner}: {count}/{total_files} wins ({percentage:.2f}%)")



def CleanUpLogs():
    try:
        shutil.rmtree(LOG_FOLDER_NAME)
    except FileNotFoundError:
        pass



def RunGames(bot_1, name_1, bot_2 ,name_2,runs=30, threads=5):
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


if __name__ == "__main__":
    # results_from_log()

    depth = 2
    maxPrestige_name     = f"MAX_Prestige_2_Moves"
    aif_MMHVR_name       = f"AIFBOT_MMHVR_{depth}_Moves"
    aif_MCTS_name        = f"AIFBOT_MCTS"
    random_name          = f"RandomBot"

    bot_maxPrestige      = MaxPrestigeBot  (bot_name=maxPrestige_name)
    bot_MMHVR_aif        = AIFBot_MMHVR    (bot_name=aif_MMHVR_name, depth=depth)
    bot_aif_MCTS         = AIFBotMCTS      (bot_name=aif_MCTS_name)
    bot_random           = RandomBot       (bot_name=random_name)

    CleanUpLogs()
    RunGames(bot_aif_MCTS, aif_MCTS_name, bot_maxPrestige, maxPrestige_name, runs=RUN_NUM, threads=THREAD_NUM)

