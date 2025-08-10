from datetime import datetime
import os

from scripts_of_tribute.board import EndGameState, GameState

from Helper import LOG_FOLDER_NAME, LOG_ENABLED_FILE, LOG_ENABLED_PRINT


def LogEndOfGame(bot_name:str, end_game_state: EndGameState, final_state: GameState):
    if not LOG_ENABLED_FILE:
        return
    os.makedirs(LOG_FOLDER_NAME, exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{bot_name}_{current_time}_{end_game_state.winner}.log"
    filepath = os.path.join(LOG_FOLDER_NAME, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== Game Ended ===\n")
            f.write(f"Winner: {end_game_state.winner}\n")
            f.write(f"Reason: {end_game_state.reason}\n")
            f.write(f"Context: {end_game_state.AdditionalContext}\n\n")
            f.write("=== Completed Actions ===\n")

            for action in final_state.completed_actions:
                f.write(action + "\n")

        PrintLog(f"INFO", f"Game log saved to: {filepath}",0)

    except Exception as e:
        PrintLog("ERROR",f"Failed to save game log: {e}",0)
        
        
        

def PrintLog(logType: str,logMessage: str, tab_count: int = 0):
    if not LOG_ENABLED_PRINT:
        return
    tabs = "\t" * tab_count
    print(f"{tabs}[{logType:^{8}}] -> {logMessage}")
