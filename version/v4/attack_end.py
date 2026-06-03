import time
import os
import random  # --- NEW: Import random module
from config import find_and_click

def return_home():
    print(" [End] Cleaning up battle...")
    
    for _ in range(3): 
        if find_and_click("surrender.png") or find_and_click("end_battle.png"):
            # --- NEW: Random pause before confirming the surrender pop-up ---
            time.sleep(random.uniform(0.7, 1.2))
            
            find_and_click("okay.png")
            
            # --- NEW: Random wait for the battle summary screen to transition ---
            time.sleep(random.uniform(1.8, 3.2))
            break
        
        # Randomize the retry interval if it misses the button on the first loop
        time.sleep(random.uniform(0.8, 1.4))

    print(" [End] Returning to home village...")
    
    # Keep trying to click return home or okay, but with human-like intervals
    while not (find_and_click("return_home.png") or find_and_click("okay.png")):
        time.sleep(random.uniform(0.8, 1.3))

    print(" [End] Successfully returned home.")
    
    # Delete the calibration image to keep things clean
    if os.path.exists("img/calibration_screen.png"):
        os.remove("img/calibration_screen.png")
        os.remove("img/debug_gold.png")
        os.remove("img/debug_elixir.png")
        # os.remove("img/debug_home_elixir.png")
        # os.remove("img/debug_home_gold.png")
        print(" [End] Deleted Attack images.")
        

    # --- NEW: Wait a random amount of time for the home village to fully render ---
    # Sometimes it loads fast, sometimes it takes a few seconds. This covers both.
    time.sleep(random.uniform(3.5, 5.5))