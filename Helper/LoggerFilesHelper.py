import os
import shutil
from collections import Counter

from Helper import LOG_FOLDER_NAME


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

