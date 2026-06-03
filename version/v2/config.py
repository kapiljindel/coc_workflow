import cv2
import numpy as np
import os
import pytesseract
from ppadb.client import Client as AdbClient

# --- VARIABLES ---
ADB_PORT = 5555
ASSETS_PATH = "assets"
pytesseract.pytesseract.tesseract_cmd = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'

# Moved both boxes UP so they frame the text perfectly!
GOLD_REGION = (125, 160, 75, 250) 
ELIXIR_REGION = (165, 200, 75, 250)

MINIMUM_GOLD = 30000
MINIMUM_ELIXIR = 30000

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

def _extract_number(screen, region):
    """Helper function to read a specific box area"""
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]
    bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    text = pytesseract.image_to_string(thresh, config='--psm 7 -c tessedit_char_whitelist=0123456789 ')
    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0

def read_loot():
    """Reads both Gold and Elixir in one screenshot"""
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    gold = _extract_number(screen, GOLD_REGION)
    elixir = _extract_number(screen, ELIXIR_REGION)
    
    return gold, elixir

def save_debug_screenshot():
    """Takes a screenshot and draws BOTH red boxes."""
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    # Draw Gold Box
    gy1, gy2, gx1, gx2 = GOLD_REGION
    cv2.rectangle(screen, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)
    cv2.putText(screen, "GOLD", (gx1, gy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Draw Elixir Box
    ey1, ey2, ex1, ex2 = ELIXIR_REGION
    cv2.rectangle(screen, (ex1, ey1), (ex2, ey2), (255, 0, 255), 2) # Purple box for Elixir!
    cv2.putText(screen, "ELIXIR", (ex1, ey1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
    
    cv2.imwrite("calibration_screen.png", screen)
    print(" [Debug] Saved dual calibration_screen.png.")