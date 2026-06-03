import cv2
import numpy as np
import time
import os
from ppadb.client import Client as AdbClient

# --- 1. CONFIGURATION ---
ADB_PORT = 5556 # Kept your updated port!
ASSETS_PATH = "assets"

def get_device():
    client = AdbClient(host="127.0.0.1", port=5037)
    client.remote_connect("127.0.0.1", ADB_PORT)
    device = client.device(f"127.0.0.1:{ADB_PORT}")
    return device

device = get_device()
if not device:
    print(f"Error: Could not connect to BlueStacks on port {ADB_PORT}. Check settings!")
    exit()

# --- 2. VISION FUNCTIONS ---
def find_and_click(image_name, threshold=0.8, click=True):
    """Searches for an asset on screen. Returns True if found."""
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    
    if template is None:
        # Silenced the warning so it doesn't spam your terminal
        return False

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        if click:
            h, w = template.shape[:-1]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            device.shell(f"input tap {center_x} {center_y}")
            print(f" [+] Action: Clicked {image_name} (Confidence: {max_val:.2f})")
        return True
    return False

# --- 3. THE MAIN BOT LOOP ---

print("--- CoC Bot Active ---")
print("Make sure Clash of Clans is open in the 64-bit BlueStacks instance.")

has_deployed = False # The memory lock!

while True:
    # State 1: In Home Village?
    if find_and_click("main_attack.png"):
        has_deployed = False
        time.sleep(1.5)
        continue
    # State 2: In Attack Menu? Find a Multiplayer Match.
    if find_and_click("find_match.png"):
        print(" [!] Next ...")
        time.sleep(5) # Wait for clouds
        continue
    # State 2: Attack Menu
    if find_and_click("single_player_attack.png"):
        print(" [!] Loading Single Player base...")
        time.sleep(4) 
        continue

    # State 3: Deploying Troops using your new logic!
    if not has_deployed and find_and_click("barbarian.png"):
        print(" [!] Base Found! Starting deployment stream...")
        time.sleep(0.5)
        
        drop_x = 150 # Starting X coordinate for drops
        
        # Keep looping and tapping UNTIL the gray icon appears
        # We set click=False because we just want to look at the gray icon, not click it
        while not find_and_click("end_barbarian.png", threshold=0.85, click=False):
            device.shell(f"input tap {drop_x} 300")
            
            # Move the tap over slightly so they don't all drop on one pixel
            drop_x += 20 
            if drop_x > 700: 
                drop_x = 150 # Reset to the left if we go too far right
                
            time.sleep(0.1) # Super fast deployment
            
        print(" [!] Troops exhausted! (Gray icon detected). Waiting for battle end...")
        has_deployed = True
        time.sleep(5)
        continue

    # State 4: Battle Cleanup
    if has_deployed:
        if find_and_click("end_battle.png") or find_and_click("surrender.png"):
            time.sleep(1)
            find_and_click("okay.png")
            has_deployed = False
            continue

    # State 5: Return Home
    if find_and_click("return_home.png") or find_and_click("okay.png"):
        print(" [!] Returning to home village.")
        has_deployed = False
        time.sleep(3)
        continue

    time.sleep(0.5)