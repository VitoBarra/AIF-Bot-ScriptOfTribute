from datetime import datetime
import os

from scripts_of_tribute.board import EndGameState, GameState

from Helper import LOG_FOLDER_NAME


def LogEndOfGame(bot_name:str, end_game_state: EndGameState, final_state: GameState):
    # Example how you can log your game for further analysis
    log_dir = LOG_FOLDER_NAME
    os.makedirs(log_dir, exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{bot_name}_{current_time}_{end_game_state.winner}.log"
    filepath = os.path.join(log_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== Game Ended ===\n")
            f.write(f"Winner: {end_game_state.winner}\n")
            f.write(f"Reason: {end_game_state.reason}\n")
            f.write(f"Context: {end_game_state.AdditionalContext}\n\n")
            f.write("=== Completed Actions ===\n")

            for action in final_state.completed_actions:
                f.write(action + "\n")

        print(f"[INFO] Game log saved to: {filepath}")

    except Exception as e:
        print(f"[ERROR] Failed to save game log: {e}")