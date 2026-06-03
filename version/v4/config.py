import cv2
import numpy as np
import os
import pytesseract
from ppadb.client import Client as AdbClient
import random  
import time    
from datetime import datetime

# --- VARIABLES ---
ADB_PORT = 5555
ASSETS_PATH = "assets"
pytesseract.pytesseract.tesseract_cmd = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'

# Loot Values
MINIMUM_GOLD = 0
MINIMUM_ELIXIR = 0
TOTAL_TROOPS = 55  

# Loot Regions (from your perfect calibration)
GOLD_REGION = (125, 160, 75, 250) 
ELIXIR_REGION = (165, 200, 75, 250)

# (SMALL_Y, BIG_Y, SMALL_X, BIG_X)
DAMAGE_REGION = (620, 700, 1350, 1580)
TROOP_REGION = (738, 768, 150, 250)

# Home Village Storage Coordinates (Top Right)
HOME_GOLD_REGION = (32, 73, 1300, 1510)     
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

# Maximum Storage Capacity
MAX_GOLD = 16000 
MAX_ELIXIR = 36500

# --- NEW: ARMY SLOTS ---
# (SMALL_Y, BIG_Y, SMALL_X, BIG_X) -> Top, Bottom, Left, Right
ARMY_SLOTS = {
    "troop_1": (745, 883, 123, 235),
    "troop_2": (745, 883, 260, 370),
    "hero_1":  (745, 883, 377, 487),
    "hero_2":  (745, 883, 534, 580),
    "hero_3":  (745, 883, 641, 690),
    "hero_4":  (745, 883, 808, 800),
    "spell_1": (745, 883, 945, 910),
    "spell_2": (745, 883, 1082, 1020),
}

# --- CONNECTION ---
client = AdbClient(host="127.0.0.1", port=5037)
client.remote_connect("127.0.0.1", ADB_PORT)
device = client.device(f"127.0.0.1:{ADB_PORT}")

if not device:
    print(f"Error: Could not connect to BlueStacks on port {ADB_PORT}.")
    exit()

# --- LOGGING SETUP ---
LOG_BUFFER = {
    "resources": [],
    "attack": [],
    "errors": [],
    "buttons": []
}

def add_log(category, message):
    """Adds a timestamped message to the buffer."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    LOG_BUFFER[category].append(f"[{timestamp}] {message}")

def flush_logs():
    """Writes all buffered logs to separate files in the /logs folder."""
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for category, lines in LOG_BUFFER.items():
        if lines:
            file_path = f"logs/{date_str}_{category}.txt"
            with open(file_path, "a") as f:
                f.write("\n".join(lines) + "\n")
            LOG_BUFFER[category] = []
    print(" [System] All logs saved to /logs/ folder.")

# --- VISION TOOLS & CLICKING ---
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
            
            # Create a 15% margin so it doesn't click the absolute edge
            margin_x = max(1, int(w * 0.15))
            margin_y = max(1, int(h * 0.15))
            
            # Pick a random coordinate strictly inside the "safe" zone of the button
            random_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
            random_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
            
            # Add a tiny random pause before the tap (human reaction time)
            time.sleep(random.uniform(0.15, 0.45))
            
            # Send the randomized tap command via ADB
            device.shell(f"input tap {random_x} {random_y}")
            print(f" [+] Clicked {image_name} at random coords: ({random_x}, {random_y})")
            
            # Log the tap
            add_log("buttons", f"Clicked {image_name} at ({random_x}, {random_y})")
            
        return True
    return False

# --- OCR NUMBER EXTRACTION ---
def _extract_number(screen, region, debug_filename, psm_mode=7):
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]
    
    if crop.size == 0:
        print(f" [!] Warning: Crop area is empty for region {region}.")
        return 0
        
    bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Ensure img folder exists before saving debug files
    if not os.path.exists("img"):
        os.makedirs("img")
        
    cv2.imwrite(debug_filename, thresh)
    
    config_str = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789% '
    text = pytesseract.image_to_string(thresh, config=config_str)
    
    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0

def read_troops():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    return _extract_number(screen, TROOP_REGION, "img/debug_troops.png")

def read_loot():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    gold = _extract_number(screen, GOLD_REGION, "img/debug_gold.png")
    elixir = _extract_number(screen, ELIXIR_REGION, "img/debug_elixir.png")
    return gold, elixir

def read_damage():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    return _extract_number(screen, DAMAGE_REGION, "img/debug_damage.png")

# --- DEBUG & CALIBRATION DRAWING ---
def save_debug_screenshot():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # Draw existing regions
    gy1, gy2, gx1, gx2 = GOLD_REGION
    cv2.rectangle(screen, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)
    
    ey1, ey2, ex1, ex2 = ELIXIR_REGION
    cv2.rectangle(screen, (ex1, ey1), (ex2, ey2), (255, 0, 255), 2) 
    
    dy1, dy2, dx1, dx2 = DAMAGE_REGION
    cv2.rectangle(screen, (dx1, dy1), (dx2, dy2), (0, 255, 0), 2)
    
    ty1, ty2, tx1, tx2 = TROOP_REGION
    cv2.rectangle(screen, (tx1, ty1), (tx2, ty2), (255, 255, 0), 2) 
    cv2.putText(screen, "TROOPS", (tx1, ty1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # --- Draw all 8 Army Slots perfectly ---
    for slot_name, coords in ARMY_SLOTS.items():
        sy1, sy2, sx1, sx2 = coords
        cv2.rectangle(screen, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
        cv2.putText(screen, slot_name, (sx1, sy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    # Ensure img directory exists
    if not os.path.exists("img"):
        os.makedirs("img")
        
    cv2.imwrite("img/calibration_screen.png", screen)
    print(" [+] Calibration screenshot saved with all 8 Army Slots highlighted!")