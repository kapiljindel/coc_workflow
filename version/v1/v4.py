import cv2
import numpy as np
import time
import os
import random # We need this for the random drop locations!
from ppadb.client import Client as AdbClient

# --- 1. CONFIGURATION ---
ADB_PORT = 5556 
ASSETS_PATH = "assets"

def get_device():
    client = AdbClient(host="127.0.0.1", port=5037)
    client.remote_connect("127.0.0.1", ADB_PORT)
    device = client.device(f"127.0.0.1:{ADB_PORT}")
    return device

device = get_device()
if not device:
    print(f"Error: Could not connect to BlueStacks on port {ADB_PORT}.")
    exit()

# --- 2. VISION FUNCTIONS ---
def find_and_click(image_name, threshold=0.8, click=True):
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    
    if template is None:
        return False

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        if click:
            h, w = template.shape[:-1]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            device.shell(f"input tap {center_x} {center_y}")
            print(f" [+] Action: Clicked {image_name}")
        return True
    return False

# --- 3. THE STRICT SEQUENCE BOT ---

print("--- CoC Strict 7-Step Bot Active ---")

# We start at step 1 and force it to go in order.
step = 1 

while True:
    
    # 1st: Main attack button
    if step == 1:
        if find_and_click("main_attack.png"):
            print(" [Step 1] Opened Map")
            step = 2
            time.sleep(1)

    # 2nd: Find a match button
    elif step == 2:
        if find_and_click("find_match.png"):
            print(" [Step 2] Clicked Find Match")
            step = 3
            time.sleep(1.5)

    # 3rd: Attack button (single_player_attack.png)
    elif step == 3:
        if find_and_click("single_player_attack.png"):
            print(" [Step 3] Commencing Attack! Loading base...")
            step = 4
            time.sleep(5) # Wait for clouds/base to load

    # 4th & 5th: Deploy Barbarians randomly/fast and wait for end_barbarian
    elif step == 4:
        if find_and_click("barbarian.png"):
            print(" [Step 4] Deploying Barbarians FAST and RANDOMLY!")
            time.sleep(0.2)
            
            # This loop checks for the gray icon. 
            while not find_and_click("end_barbarian.png", threshold=0.85, click=False):
                
                # Burst Fire: Drop 10 troops instantly before checking the screen again
                for _ in range(10):
                    # Random coordinates on the upper-left grass edge
                    rand_x = random.randint(100, 600) 
                    rand_y = random.randint(100, 250)
                    device.shell(f"input tap {rand_x} {rand_y}")
                    # Notice there is NO time.sleep here. Maximum speed!

            print(" [Step 5] end_barbarian detected! All troops deployed.")
            print("         Waiting for battle to finish...")
            step = 6
            time.sleep(8) # Let the battle play out for a bit

    # 6th: Surrender and press okay
    elif step == 6:
        if find_and_click("surrender.png") or find_and_click("end_battle.png"):
            print(" [Step 6] Surrendering...")
            time.sleep(1)
            if find_and_click("okay.png"):
                step = 7
                time.sleep(2)

    # 7th: Return home
    elif step == 7:
        if find_and_click("return_home.png") or find_and_click("okay.png"):
            print(" [Step 7] Returning Home. Cycle Complete!")
            step = 1 # Reset back to Step 1 for the next run!
            print("\n--- Starting New Attack Cycle ---")
            time.sleep(3)

    # Small safety delay so the loop doesn't crash your CPU
    time.sleep(0.5)