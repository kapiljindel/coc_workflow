import time
from config import find_and_click

def go_to_base():
    print("\n [Start] Opening Map...")
    # Keep trying until it successfully clicks the attack button
    while not find_and_click("main_attack.png"):
        time.sleep(1)

    time.sleep(1.5)

    print(" [Start] Clicking Find Match...")
    while not find_and_click("find_match.png"):
        time.sleep(1)

    print(" [Start] Clicking Attack Button...")
    while not find_and_click("single_player_attack.png"):
        time.sleep(1)

    print(" [Start] Searching the clouds...")
    time.sleep(6) # Wait for the first base to load