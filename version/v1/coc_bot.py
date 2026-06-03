import cv2
import numpy as np
import time
import os
from ppadb.client import Client as AdbClient

# --- 1. CONFIGURATION ---
# IMPORTANT: Check your BlueStacks Settings -> Advanced for the current ADB port
ADB_PORT = 5556 
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
    # Capture screen
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # Load template
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    
    if template is None:
        print(f"Warning: File {template_path} not found!")
        return False

    # Match Template
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

while True:
    # State 1: In Home Village? Start the attack process.
    if find_and_click("main_attack.png"):
        time.sleep(1.5)
        continue

    # State 2: In Attack Menu? Find a Multiplayer Match.
    if find_and_click("find_match.png"):
        print(" [!] Next ...")
        time.sleep(5) # Wait for clouds
        continue

    if find_and_click("single_player_attack.png"):
        print(" [!] Searching for an opponent...")
        time.sleep(5) # Wait for clouds
        continue

    # State 3: Looking at an Enemy Base? 
    # If we see the Barbarian icon, we are ready to deploy!
    if find_and_click("barbarian.png"):
        print(" [!] Base Found! Starting deployment...")
        time.sleep(0.5)
        
        # Simple Deployment Strategy: 
        # Click the barbarian icon again to ensure it's selected, 
        # then tap several spots on the outer grass.
        for i in range(10):
            # Tapping different spots to avoid "clustering"
            x_coord = 200 + (i * 40)
            y_coord = 200
            device.shell(f"input tap {x_coord} {y_coord}")
            time.sleep(0.1)
        
        print(" [!] Troops deployed. Watching for battle end...")
        time.sleep(10) # Wait a bit before checking for "End" buttons
        continue

    # State 4: Battle Cleanup
    # These will trigger when the battle naturally ends or troops are gone
    if find_and_click("end_battle.png") or find_and_click("surrender.png"):
        time.sleep(1)
        find_and_click("okay.png")
        continue

    if find_and_click("return_home.png") or find_and_click("okay.png"):
        print(" [!] Returning to home village.")
        time.sleep(3)
        continue

    # Small delay to prevent CPU maxing out
    time.sleep(1)