import cv2
import numpy as np
import os
import pytesseract
from ppadb.client import Client as AdbClient

# --- VARIABLES ---
ADB_PORT = 5555
ASSETS_PATH = "assets"
pytesseract.pytesseract.tesseract_cmd = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'

#Loot Values (you can set these to 0 if you just want to read the values without dumping excess loot)
MINIMUM_GOLD = 0
MINIMUM_ELIXIR = 0

# Loot Regions (from your perfect calibration)
GOLD_REGION = (125, 160, 75, 250) 
ELIXIR_REGION = (165, 200, 75, 250)

# Pushed WAY to the right, and down slightly
# (1,2,3,4,) = (top {increase for down} , down, left, right)
# # (SMALL_Y, BIG_Y, SMALL_X, BIG_X)

DAMAGE_REGION = (620, 700, 1350, 1580)
TROOP_REGION = (738, 768, 150, 250)

# --- NEW: Home Village Storage Coordinates (Top Right) ---
HOME_GOLD_REGION = (32, 73, 1300, 1510)     
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

# --- NEW: Maximum Storage Capacity ---
# Change these to match your actual max storage limits!
MAX_GOLD = 16000 
MAX_ELIXIR = 36500





# --- CONNECTION ---
client = AdbClient(host="127.0.0.1", port=5037)
client.remote_connect("127.0.0.1", ADB_PORT)
device = client.device(f"127.0.0.1:{ADB_PORT}")

if not device:
    print(f"Error: Could not connect to BlueStacks on port {ADB_PORT}.")
    exit()

# --- VISION TOOLS ---
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
            print(f" [+] Clicked {image_name}")
        return True
    return False

# --- NEW: Function to read the troop count ---
def read_troops():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # We use the exact same extraction logic, but save it as debug_troops.png
    return _extract_number(screen, TROOP_REGION, "debug_troops.png")

# --- FIXED: Added 'psm_mode=7' as a default argument! ---
# If a file forgets to send the PSM mode, it will just default to 7 safely.
def _extract_number(screen, region, debug_filename, psm_mode=7):
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]
    
    if crop.size == 0:
        print(f" [!] Warning: Crop area is empty for region {region}.")
        return 0
        
    bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    cv2.imwrite(debug_filename, thresh)
    
    config_str = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789% '
    text = pytesseract.image_to_string(thresh, config=config_str)
    
    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0

def read_loot():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # Pass custom filenames so they don't overwrite each other
    gold = _extract_number(screen, GOLD_REGION, "debug_gold.png")
    elixir = _extract_number(screen, ELIXIR_REGION, "debug_elixir.png")
    return gold, elixir

def read_damage():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # Pass the custom filename for damage
    return _extract_number(screen, DAMAGE_REGION, "debug_damage.png")

def save_debug_screenshot():
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    gy1, gy2, gx1, gx2 = GOLD_REGION
    cv2.rectangle(screen, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)
    
    ey1, ey2, ex1, ex2 = ELIXIR_REGION
    cv2.rectangle(screen, (ex1, ey1), (ex2, ey2), (255, 0, 255), 2) 
    
    dy1, dy2, dx1, dx2 = DAMAGE_REGION
    cv2.rectangle(screen, (dx1, dy1), (dx2, dy2), (0, 255, 0), 2)
    
    # --- NEW: Draw the Cyan Troop Box (BGR color format) ---
    ty1, ty2, tx1, tx2 = TROOP_REGION
    cv2.rectangle(screen, (tx1, ty1), (tx2, ty2), (255, 255, 0), 2) 
    cv2.putText(screen, "TROOPS", (tx1, ty1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    cv2.imwrite("calibration_screen.png", screen)