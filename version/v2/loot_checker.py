import time
import os
from config import find_and_click, read_loot, MINIMUM_GOLD, MINIMUM_ELIXIR, save_debug_screenshot

def evaluate_base():
    time.sleep(2) # Buffer for clouds to clear
    print(" [Scout] Base loaded. Scanning loot...")
    
    save_debug_screenshot()
    
    current_gold, current_elixir = read_loot()
    print(f"         Detected Gold: {current_gold:,} | Elixir: {current_elixir:,}")
    
    if current_gold >= MINIMUM_GOLD or current_elixir >= MINIMUM_ELIXIR:
        print("         JACKPOT! Calling in the troops.")
        return True # Tell the main script to attack!
        
    else:
        print("         Trash base. Cleaning up and Clicking Next...")
        if os.path.exists("calibration_screen.png"):
            os.remove("calibration_screen.png")

        if find_and_click("next_base.png"):
            time.sleep(7) 
            return False # Tell the main script we are still searching
        else:
            print("         [!] 'Next' button missing! Timer likely expired.")
            return True # Force an attack/cleanup so we don't get stuck