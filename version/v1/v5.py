import cv2
import numpy as np
import time
import os
import random
import pytesseract # The new reading engine!
from ppadb.client import Client as AdbClient

# --- 1. CONFIGURATION ---
ADB_PORT = 5556 
ASSETS_PATH = "assets"

# Tell Python exactly where you installed Tesseract
pytesseract.pytesseract.tesseract_cmd = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'
# tesseract-ocr-w64-setup-5.4.0.20240606.exe
# --- LOOT CONFIGURATION ---
MINIMUM_GOLD = 15000 

# [Y_START : Y_END, X_START : X_END]
# You will likely need to tweak these numbers to perfectly crop the Gold amount!
# Right now, it looks at the top-left area of a standard 1080p screen.
# Format: (Y_START, Y_END, X_START, X_END)
# LOOT_REGION = (80, 130, 100, 300)
LOOT_REGION = (130, 180, 50, 250)
def get_device():
    client = AdbClient(host="127.0.0.1", port=5037)
    client.remote_connect("127.0.0.1", ADB_PORT)
    return client.device(f"127.0.0.1:{ADB_PORT}")

device = get_device()

# --- 2. VISION FUNCTIONS ---
def find_and_click(image_name, threshold=0.8, click=True):
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    if template is None: return False

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        if click:
            h, w = template.shape[:-1]
            device.shell(f"input tap {max_loc[0] + w // 2} {max_loc[1] + h // 2}")
            print(f" [+] Action: Clicked {image_name}")
        return True
    return False

def read_gold_amount():
    """Takes a screenshot, crops, UPSCALES, and reads the number."""
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # 1. Safely unpack the tuple and crop the screen
    y1, y2, x1, x2 = LOOT_REGION
    cropped_gold = screen[y1:y2, x1:x2]
    
    # 2. Magnifying Glass: Resize the image to make it 3x bigger
    # This makes the thick black outlines much easier for the computer to understand
    bigger = cv2.resize(cropped_gold, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    # 3. Process image to make text pop
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    
    # Simple thresholding: Forces bright text to turn black, and background to turn white
    # Tesseract prefers reading black text on a white background!
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # 4. Save the debug image so you can see the new massive text!
    cv2.imwrite("debug_loot_crop.png", thresh)
    
    # 5. Use Tesseract to read the numbers (added a space to the whitelist!)
    text = pytesseract.image_to_string(thresh, config='--psm 7 -c tessedit_char_whitelist=0123456789 ')
    
    # Clean up the text and convert to integer
    clean_text = ''.join(filter(str.isdigit, text))
    if clean_text == "":
        return 0
    return int(clean_text)

# --- 3. THE SMART FARMING BOT ---

print("--- CoC Smart Farming Bot Active ---")
step = 1 

while True:
    if step == 1:
        if find_and_click("main_attack.png"):
            print(" [Step 1] Opened Map")
            step = 2
            time.sleep(1)

    elif step == 2:
        # Changed back to find_match so we can farm multiplayer!
        if find_and_click("find_match.png"):
            print(" [Step 2] Searching the clouds...")
            step = 3
            time.sleep(6) 

    elif step == 3:
        # We are on an enemy base. Let's check the loot!
        print(" [Step 3] Base loaded. Scanning loot...")
        current_gold = read_gold_amount()
        print(f"         Detected Gold: {current_gold:,}")
        
        if current_gold >= MINIMUM_GOLD:
            print(f"         JACKPOT! Proceeding to attack.")
            step = 4
        else:
            print(f"         Trash base. Clicking Next...")
            if find_and_click("next_base.png"):
                time.sleep(5) # Wait for clouds again, STAY in step 3!

    elif step == 4:
        if find_and_click("barbarian.png"):
            print(" [Step 4] Deploying Swarm...")
            time.sleep(0.2)
            while not find_and_click("end_barbarian.png", threshold=0.85, click=False):
                for _ in range(10):
                    device.shell(f"input tap {random.randint(100, 600)} {random.randint(100, 250)}")
            print(" [Step 5] Troops exhausted. Waiting for battle to finish...")
            step = 6
            time.sleep(8) 

    elif step == 6:
        if find_and_click("surrender.png") or find_and_click("end_battle.png"):
            time.sleep(1)
            if find_and_click("okay.png"):
                step = 7
                time.sleep(2)

    elif step == 7:
        if find_and_click("return_home.png") or find_and_click("okay.png"):
            print(" [Step 7] Returning Home. Cycle Complete!")
            step = 1 
            time.sleep(3)

    time.sleep(0.5)