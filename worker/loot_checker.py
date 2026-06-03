import time
import os
import random  # --- NEW: Import random module
from config import find_and_click, read_loot, MINIMUM_GOLD, MINIMUM_ELIXIR, save_debug_screenshot

def evaluate_base():
    # --- NEW: Human reaction time. Simulates a player looking at the screen 
    # to read the loot numbers before doing anything.
    time.sleep(random.uniform(1.8, 3.5)) 
    
    print(" [Scout] Base loaded. Scanning loot...")
    save_debug_screenshot()
    
    current_gold, current_elixir = read_loot()
    print(f"        Detected Gold: {current_gold:,} | Elixir: {current_elixir:,}")
    
    if current_gold >= MINIMUM_GOLD or current_elixir >= MINIMUM_ELIXIR:
        print("        JACKPOT! Calling in the troops.")
        # We are returning the gold and elixir numbers back to main.py!
        return True, current_gold, current_elixir 
        
    else:
        print("        Trash base. Cleaning up and Clicking Next...")
        if os.path.exists("calibration_screen.png"):
            os.remove("calibration_screen.png")

        # Your updated config.py already randomizes the coordinates for this click!
        if find_and_click("next_base.png"):
            # --- NEW: Randomized cloud wait time. Clouds vary, but this stops the 
            # bot from initiating its next action at the exact same millisecond mark.
            time.sleep(random.uniform(5.5, 8.5)) 
            return False, 0, 0 # Return zeros since we aren't attacking
        else:
            print("        [!] 'Next' button missing! Timer likely expired.")
            return True, current_gold, current_elixir