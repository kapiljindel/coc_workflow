import time
import random  
import pyautogui  # <-- NEW: Used for clicking exact X, Y coordinates

# =====================================================================
# CONFIGURATION: REPLACE THESE WITH YOUR ACTUAL SCREEN COORDINATES (X, Y)
# =====================================================================
MAP_BUTTON_COORD = (150, 850)        # Coordinates for main_attack button
FIND_MATCH_COORD = (950, 700)        # Coordinates for find_match button
ATTACK_BUTTON_COORD = (1100, 500)    # Coordinates for single_player_attack button
# =====================================================================

def click_point(coordinates):
    """Helper function to click a coordinate with a slight natural human delay"""
    x, y = coordinates
    pyautogui.click(x, y)
    print(f" [Action] Clicked point: ({x}, {y})")

def go_to_base():
    print("\n [Start] Opening Map...")
    # Click the map/attack button
    click_point(MAP_BUTTON_COORD)
    
    # Wait for the map UI to fully open and animate
    time.sleep(random.uniform(1.5, 2.5))

    print(" [Start] Clicking Find Match...")
    # Click the find match button
    click_point(FIND_MATCH_COORD)

    # Human-like micro-pause before moving the mouse/clicking the next button
    time.sleep(random.uniform(0.6, 1.1))

    print(" [Start] Clicking Attack Button...")
    # Click the final single player attack button
    click_point(ATTACK_BUTTON_COORD)

    print(" [Start] Searching the clouds...")
    # Generous sleep to let the cloud loading screen pass
    time.sleep(random.uniform(5.5, 8.0))
    
    return True # Success!