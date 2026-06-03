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
DAMAGE_REGION = (620, 700, 1350, 1580)
TROOP_REGION = (738, 768, 150, 250)

# Home Village Storage Coordinates (Top Right)
HOME_GOLD_REGION = (32, 73, 1300, 1510)     
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

MAX_GOLD = 160000000000 
MAX_ELIXIR = 365000000000000

# ==========================================
# --- YOUR DYNAMIC ARMY LOADOUT ---
# ==========================================
# Define your army here! You MUST include "category" (troop, hero, or spell) 
# so the bot knows how much space to put between the boxes!
MY_ARMY = [
    {"name": "dragon", "category": "troop", "count": 9},
    {"name": "king",   "category": "hero",  "count": 1},
    {"name": "queen",  "category": "hero",  "count": 1},
    {"name": "freeze", "category": "spell", "count": 5},
    {"name": "rage",   "category": "spell", "count": 1},
]

def generate_army_slots():
    """Mathematically calculates the exact pixel boxes for the army bar."""
    slots = {}
    y1, y2 = 745, 883
    current_x = 123  # Starting X of the first card
    box_width = 112  # Width of a CoC card

    for i, unit in enumerate(MY_ARMY):
        slot_name = f"slot_{i+1}"
        unit["slot"] = slot_name # Inject the slot name into the army list
        
        x1 = int(current_x)
        x2 = int(current_x + box_width)
        slots[slot_name] = (y1, y2, x1, x2)
        
        # Calculate the physical gap for the NEXT card
        if i < len(MY_ARMY) - 1:
            curr_cat = unit["category"]
            next_cat = MY_ARMY[i+1]["category"]
            
            if curr_cat == next_cat:
                current_x = x2 + 10  # Small gap for same type (e.g. Hero to Hero)
            else:
                current_x = x2 + 26  # Large gap for new type (e.g. Hero to Spell)
                
    return slots

# Generate the slots instantly when the script loads!
ARMY_SLOTS = generate_army_slots()
# ==========================================

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
            margin_x = max(1, int(w * 0.15))
            margin_y = max(1, int(h * 0.15))
            random_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
            random_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
            time.sleep(random.uniform(0.15, 0.45))
            device.shell(f"input tap {random_x} {random_y}")
            add_log("buttons", f"Clicked {image_name} at ({random_x}, {random_y})")
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
    if not os.path.exists("img"): os.makedirs("img")
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
    return _extract_number(screen, GOLD_REGION, "img/debug_gold.png"), _extract_number(screen, ELIXIR_REGION, "img/debug_elixir.png")

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
    
    cv2.rectangle(screen, (GOLD_REGION[2], GOLD_REGION[0]), (GOLD_REGION[3], GOLD_REGION[1]), (0, 0, 255), 2)
    cv2.rectangle(screen, (ELIXIR_REGION[2], ELIXIR_REGION[0]), (ELIXIR_REGION[3], ELIXIR_REGION[1]), (255, 0, 255), 2) 
    cv2.rectangle(screen, (DAMAGE_REGION[2], DAMAGE_REGION[0]), (DAMAGE_REGION[3], DAMAGE_REGION[1]), (0, 255, 0), 2)
    
    # Draw dynamically generated slots
    for slot_name, coords in ARMY_SLOTS.items():
        sy1, sy2, sx1, sx2 = coords
        cv2.rectangle(screen, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
        cv2.putText(screen, slot_name, (sx1, sy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    if not os.path.exists("img"): os.makedirs("img")
    cv2.imwrite("img/ui_boxes.png", screen)
    print(" [+] UI Calibration screenshot saved as 'img/ui_boxes.png'!")