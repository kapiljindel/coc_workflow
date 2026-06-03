import time
import os
from config import find_and_click, read_loot, MINIMUM_GOLD, MINIMUM_ELIXIR, save_debug_screenshot

def evaluate_base():
    time.sleep(2)
    print(" [Scout] Base loaded. Scanning loot...")
    save_debug_screenshot()
    
    current_gold, current_elixir = read_loot()
    print(f"         Detected Gold: {current_gold:,} | Elixir: {current_elixir:,}")
    
    if current_gold >= MINIMUM_GOLD or current_elixir >= MINIMUM_ELIXIR:
        print("         JACKPOT! Calling in the troops.")
        # NEW: We are returning the gold and elixir numbers back to main.py!
        return True, current_gold, current_elixir 
        
    else:
        print("         Trash base. Cleaning up and Clicking Next...")
        if os.path.exists("calibration_screen.png"):
            os.remove("calibration_screen.png")

        if find_and_click("next_base.png"):
            time.sleep(7) 
            return False, 0, 0 # Return zeros since we aren't attacking
        else:
            print("         [!] 'Next' button missing! Timer likely expired.")
            return True, current_gold, current_elixir