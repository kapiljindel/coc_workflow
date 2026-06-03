import time
import os
from config import find_and_click

def return_home():
    print(" [End] Cleaning up battle...")
    
    for _ in range(3): 
        if find_and_click("surrender.png") or find_and_click("end_battle.png"):
            time.sleep(1)
            find_and_click("okay.png")
            time.sleep(2)
            break
        time.sleep(1)

    print(" [End] Returning to home village...")
    while not (find_and_click("return_home.png") or find_and_click("okay.png")):
        time.sleep(1)

    print(" [End] Successfully returned home.")
    
    # --- NEW: Delete the calibration image to keep things clean ---
    if os.path.exists("calibration_screen.png"):
        os.remove("calibration_screen.png")
        print(" [End] Deleted old calibration image.")
        
    time.sleep(3)