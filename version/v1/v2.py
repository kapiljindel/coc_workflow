import cv2
import numpy as np
import time
import os
from ppadb.client import Client as AdbClient

# --- 1. CONFIGURATION ---
ADB_PORT = 5556 # Make sure this matches your 64-bit instance port!
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
            print(f" [+] Clicked {image_name} (Confidence: {max_val:.2f})")
        return True
    return False

# --- 3. THE UPDATED STATE MACHINE ---

print("--- CoC Bot Active (Single Player Mode) ---")

# This is our memory variable to stop early surrenders
has_deployed = False 

while True:
    # State 1: Open the Attack Map
    if find_and_click("main_attack.png"):
        has_deployed = False # Reset memory for a new battle
        time.sleep(1.5)
        continue

    # State 2: Click the Single Player Goblin Map (Instead of Find Match)
    if find_and_click("single_player_attack.png"):
        print(" [!] Loading Single Player base...")
        time.sleep(3) # Wait for the base to load
        continue

    # State 3: Deploy Troops (ONLY if we haven't deployed yet)
    if not has_deployed and find_and_click("barbarian.png"):
        print(" [!] Base Found! Deploying troops...")
        time.sleep(0.5)
        
        # Tap multiple times to drop troops
        for i in range(15):
            x_coord = 150 + (i * 10)
            y_coord = 300
            device.shell(f"input tap {x_coord} {y_coord}")
            time.sleep(0.1)
            
        has_deployed = True # Memory updated! 
        print(" [!] Deployment finished. Waiting for battle to conclude...")
        time.sleep(8)
        continue

    # State 4: End Battle (ONLY allowed if troops were actually deployed)
    if has_deployed:
        if find_and_click("end_battle.png") or find_and_click("surrender.png"):
            time.sleep(1.5)
            find_and_click("okay.png")
            has_deployed = False # Reset for the next run
            continue

    # State 5: Return Home Screen
    if find_and_click("return_home.png"):
        print(" [!] Returning to home village.")
        has_deployed = False
        time.sleep(3)
        continue

    time.sleep(0.5)