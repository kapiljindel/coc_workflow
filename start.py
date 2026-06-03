import time
import random  
from config import find_and_click

def go_to_base():
    print("\n [Start] Opening Map...")
    attempts = 0
    while not (find_and_click("main_attack.png") or find_and_click("main_attack_low.png") or find_and_click("main_attack_4.png")):
        time.sleep(random.uniform(0.8, 1.3))
        attempts += 1
        if attempts > 15: # Timeout after ~15-20 seconds
            print(" [Error] Timeout waiting for Map button!")
            return False

    time.sleep(random.uniform(1.2, 2.1))

    print(" [Start] Clicking Find Match...")
    attempts = 0
    while not find_and_click("find_match.png"):
        time.sleep(random.uniform(0.8, 1.3))
        attempts += 1
        if attempts > 15:
            print(" [Error] Timeout waiting for Find Match button!")
            return False

    time.sleep(random.uniform(0.4, 0.9))

    print(" [Start] Clicking Attack Button...")
    attempts = 0
    while not find_and_click("single_player_attack.png"):
        time.sleep(random.uniform(0.8, 1.3))
        attempts += 1
        if attempts > 15:
            print(" [Error] Timeout waiting for Attack button!")
            return False

    print(" [Start] Searching the clouds...")
    time.sleep(random.uniform(5.5, 8.0))
    
    return True # Success!
    
    # import time
# import random  # --- NEW: Import random module
# from config import find_and_click

# def go_to_base():
#     print("\n [Start] Opening Map...")
#     # Keep trying until it successfully clicks the attack button
#     # Changed from fixed 1s to a random window between 0.8s and 1.3s
#     while not (find_and_click("main_attack.png")or find_and_click("main_attack_4.png")):

#         time.sleep(random.uniform(0.8, 1.3))

#     # Replaced the fixed 1.5s delay with a randomized transition delay
#     time.sleep(random.uniform(1.2, 2.1))

#     print(" [Start] Clicking Find Match...")
#     while not find_and_click("find_match.png"):
#         time.sleep(random.uniform(0.8, 1.3))

#     # --- NEW: Added a tiny micro-pause here. Humans rarely click two different 
#     # screen locations instantly one after the other.
#     time.sleep(random.uniform(0.4, 0.9))

#     print(" [Start] Clicking Attack Button...")
#     while not find_and_click("single_player_attack.png"):
#         time.sleep(random.uniform(0.8, 1.3))

#     print(" [Start] Searching the clouds...")
#     # Replaced the fixed 6s wait. Cloud loading times vary anyway, 
#     # but this ensures the bot doesn't trigger its next action at the exact same millisecond every time.
#     time.sleep(random.uniform(5.5, 8.0))