import cv2
import numpy as np
import os
import pytesseract
from ppadb.client import Client as AdbClient
import random  
import time    
from datetime import datetime
import json

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load config values
config = load_config()

ADB_PORT = config["ADB_PORT"]
# --- WALL UPGRADE LOGIC TOGGLE ---
IS_UPGRADE_WALL = config["IS_UPGRADE_WALL"]
MINIMUM_GOLD = config["MINIMUM_GOLD"]
MINIMUM_ELIXIR = config["MINIMUM_ELIXIR"]
TOTAL_TROOPS = config["TOTAL_TROOPS"]

MAX_GOLD = config["MAX_GOLD"]
MAX_ELIXIR = config["MAX_ELIXIR"]

# # --- VARIABLES ---
# ADB_PORT = 5555

# # Loot Values
# MINIMUM_GOLD = 400000
# MINIMUM_ELIXIR = 400000
# TOTAL_TROOPS = 30  


# MAX_GOLD = 160000000000 
# MAX_ELIXIR = 365000000000000

# ==========================================
# --- DYNAMIC ARMY LOADOUT ---
# ==========================================
MY_ARMY = config["MY_ARMY"]
# [
#     {"name": "dragon", "category": "troop", "count": 9},
#     {"name": "king",   "category": "hero",  "count": 1},
#     {"name": "queen",  "category": "hero",  "count": 1},
#     {"name": "freeze", "category": "spell", "count": 5},
#     {"name": "rage",   "category": "spell", "count": 1},
# ]

# ==========================================
# --- No Configuration Needed ---
# ==========================================

# --- NEW: PERFORMANCE TOGGLE ---
# Set to False to stop saving images to your hard drive every second!
DEBUG_MODE = True 

# --- VARIABLES ---
ASSETS_PATH = "assets"
pytesseract.pytesseract.tesseract_cmd = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'


# Home Village Storage Coordinates
HOME_GOLD_REGION = (32, 73, 1300, 1510)     
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

# Loot Regions 
GOLD_REGION = (125, 160, 75, 250) 
ELIXIR_REGION = (165, 200, 75, 250)
DAMAGE_REGION = (620, 700, 1350, 1580)
TROOP_REGION = (738, 768, 150, 250)

# ==========================================
# --- No Configuration Needed Ends ---
# ==========================================


def generate_army_slots():
    slots = {}
    y1, y2 = 745, 883
    current_x = 123  
    box_width = 112  

    for i, unit in enumerate(MY_ARMY):
        slot_name = f"slot_{i+1}"
        unit["slot"] = slot_name 
        
        x1 = int(current_x)
        x2 = int(current_x + box_width)
        slots[slot_name] = (y1, y2, x1, x2)
        
        if i < len(MY_ARMY) - 1:
            curr_cat = unit["category"]
            next_cat = MY_ARMY[i+1]["category"]
            
            if curr_cat == next_cat:
                current_x = x2 + 10  
            else:
                current_x = x2 + 26  
                
    return slots

ARMY_SLOTS = generate_army_slots()

# --- CONNECTION ---
client = AdbClient(host="127.0.0.1", port=5037)
client.remote_connect("127.0.0.1", ADB_PORT)
device = client.device(f"127.0.0.1:{ADB_PORT}")

if not device:
    print(f"Error: Could not connect to BlueStacks on port {ADB_PORT}.")
    exit()

# --- LOGGING SETUP ---
LOG_BUFFER = {"resources": [], "attack": [], "errors": [], "buttons": []}

def add_log(category, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    LOG_BUFFER[category].append(f"[{timestamp}] {message}")

def flush_logs():
    if not os.path.exists("logs"): os.makedirs("logs")
    date_str = datetime.now().strftime("%Y-%m-%d")
    for category, lines in LOG_BUFFER.items():
        if lines:
            with open(f"logs/{date_str}_{category}.txt", "a") as f:
                f.write("\n".join(lines) + "\n")
            LOG_BUFFER[category] = []
    print(" [System] All logs saved to /logs/ folder.")

# --- VISION TOOLS & CLICKING ---
def get_current_screen():
    """Takes a single screenshot and returns the CV2 image array."""
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    return cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)

def find_and_click(image_name, threshold=0.8, click=True):
    screen = get_current_screen()
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    if template is None: return False

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        if click:
            h, w = template.shape[:-1]
            margin_x = max(1, int(w * 0.15))
            margin_y = max(1, int(h * 0.15))
            random_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
            random_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
            time.sleep(random.uniform(0.15, 0.45))
            device.shell(f"input tap {random_x} {random_y}")
            add_log("buttons", f"Clicked {image_name} at ({random_x}, {random_y})")
        return True
    return False

def find_and_click_in_region(image_name, region, threshold=0.8, click=True):
    """Crops the screen to a specific region before matching to eliminate screen noise."""
    screen = get_current_screen()
    y1, y2, x1, x2 = region
    
    # Crop down to just our box area
    cropped_screen = screen[y1:y2, x1:x2]
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    template = cv2.imread(template_path)
    if template is None: return False

    result = cv2.matchTemplate(cropped_screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        if click:
            h, w = template.shape[:-1]
            margin_x = max(1, int(w * 0.15))
            margin_y = max(1, int(h * 0.15))
            
            # Math coordinates inside the crop
            random_crop_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
            random_crop_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
            
            # Convert back to absolute screen coordinates!
            final_x = x1 + random_crop_x
            final_y = y1 + random_crop_y
            
            time.sleep(random.uniform(0.15, 0.45))
            device.shell(f"input tap {final_x} {final_y}")
            add_log("buttons", f"Clicked {image_name} inside region at ({final_x}, {final_y})")
        return True
    return False

# --- OCR NUMBER EXTRACTION ---
def _extract_number(screen, region, debug_filename, psm_mode=7):
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]
    if crop.size == 0: return 0
    bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Only save to hard drive if DEBUG_MODE is True!
    if DEBUG_MODE:
        if not os.path.exists("img"): os.makedirs("img")
        cv2.imwrite(debug_filename, thresh)
        
    config_str = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789% '
    text = pytesseract.image_to_string(thresh, config=config_str)
    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0

def read_troops(screen=None):
    if screen is None: screen = get_current_screen()
    return _extract_number(screen, TROOP_REGION, "img/debug_troops.png")

def read_loot(screen=None):
    if screen is None: screen = get_current_screen()
    return _extract_number(screen, GOLD_REGION, "img/debug_gold.png"), _extract_number(screen, ELIXIR_REGION, "img/debug_elixir.png")

def read_damage(screen=None):
    if screen is None: screen = get_current_screen()
    return _extract_number(screen, DAMAGE_REGION, "img/debug_damage.png")

# --- DEBUG & CALIBRATION DRAWING ---
def save_debug_screenshot():
    if not DEBUG_MODE: return # Skip if debug is off
    
    screen = get_current_screen()
    
    cv2.rectangle(screen, (GOLD_REGION[2], GOLD_REGION[0]), (GOLD_REGION[3], GOLD_REGION[1]), (0, 0, 255), 2)
    cv2.rectangle(screen, (ELIXIR_REGION[2], ELIXIR_REGION[0]), (ELIXIR_REGION[3], ELIXIR_REGION[1]), (255, 0, 255), 2) 
    cv2.rectangle(screen, (DAMAGE_REGION[2], DAMAGE_REGION[0]), (DAMAGE_REGION[3], DAMAGE_REGION[1]), (0, 255, 0), 2)
    
    for slot_name, coords in ARMY_SLOTS.items():
        sy1, sy2, sx1, sx2 = coords
        cv2.rectangle(screen, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
        cv2.putText(screen, slot_name, (sx1, sy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    if not os.path.exists("img"): os.makedirs("img")
    cv2.imwrite("img/ui_boxes.png", screen)
    print(" [+] UI Calibration screenshot saved as 'img/ui_boxes.png'!")



# Auto Update Config Function (for future use if needed)

# Builder Menu Clicking Function ---
def click_coordinates(x, y):
    """Clicks an absolute X, Y pixel location directly inside the emulator via ADB."""
    if not device:
        print(" [Error] Cannot click coordinates. ADB device not connected.")
        return False
        
    # Add a tiny random offset (+/- 2 pixels) so anti-cheat doesn't flag identical clicks
    random_x = x + random.randint(-2, 2)
    random_y = y + random.randint(-2, 2)
    
    time.sleep(random.uniform(0.15, 0.35))
    device.shell(f"input tap {random_x} {random_y}")
    add_log("buttons", f"Clicked absolute coordinates ({random_x}, {random_y})")
    return True    


    # List reader

# Format: (y1, y2, x1, x2)
BUILDER_LIST_REGION = (124, 685, 600, 1038)


def save_debug_screenshot():
    if not DEBUG_MODE: return # Skip if debug is off
    
    screen = get_current_screen()
    
    # Draw your existing boxes
    cv2.rectangle(screen, (GOLD_REGION[2], GOLD_REGION[0]), (GOLD_REGION[3], GOLD_REGION[1]), (0, 0, 255), 2)
    cv2.rectangle(screen, (ELIXIR_REGION[2], ELIXIR_REGION[0]), (ELIXIR_REGION[3], ELIXIR_REGION[1]), (255, 0, 255), 2) 
    cv2.rectangle(screen, (DAMAGE_REGION[2], DAMAGE_REGION[0]), (DAMAGE_REGION[3], DAMAGE_REGION[1]), (0, 255, 0), 2)
    
    # --- NEW: Draw the Builder Dropdown List Box ---
    cv2.rectangle(screen, (BUILDER_LIST_REGION[2], BUILDER_LIST_REGION[0]), (BUILDER_LIST_REGION[3], BUILDER_LIST_REGION[1]), (255, 0, 0), 2)
    cv2.putText(screen, "BUILDER_LIST", (BUILDER_LIST_REGION[2], BUILDER_LIST_REGION[0] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    for slot_name, coords in ARMY_SLOTS.items():
        sy1, sy2, sx1, sx2 = coords
        cv2.rectangle(screen, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
        cv2.putText(screen, slot_name, (sx1, sy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    if not os.path.exists("img"): os.makedirs("img")
    cv2.imwrite("img/ui_boxes.png", screen)
    print(" [+] UI Calibration screenshot saved as 'img/ui_boxes.png'!")

# Scroll Code 
def scroll_down_builder_menu(region, loops=2):
    """
    Drags the menu up to scroll down, staying STRICTLY inside 
    the boundaries of the calibrated blue box.
    """
    if not device:
        print(" [Error] ADB device not connected.")
        return
        
    # Unpack your perfectly calibrated box coordinates
    y1, y2, x1, x2 = region
    
    # 1. Calculate the exact horizontal center of your blue box
    start_x = (x1 + x2) // 2
    end_x = start_x
    
    # 2. Calculate safe starting and ending points inside the box borders
    # (Subtract/add 40 pixels to ensure the touch gesture doesn't clip the outer frame lines)
    start_y = y2 - 40  # Safe bottom area inside the box
    end_y = y1 + 40    # Safe top area inside the box
    duration = 800     # 800ms controlled swipe speed

    for i in range(loops):
        print(f" [Engine] Scrolling inside box (Swipe up from Y:{start_y} to Y:{end_y})...")
        device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
        time.sleep(0.6) # Let the scrolling momentum come to a full stop