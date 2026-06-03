import cv2
import numpy as np
import pytesseract
# --- NEW: Imported your MAX limits from config ---
from config import device, HOME_GOLD_REGION, HOME_ELIXIR_REGION, MAX_GOLD, MAX_ELIXIR

def _extract_home_number(screen, region, debug_filename):
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]
    
    if crop.size == 0:
        return 0
        
    bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    cv2.imwrite(debug_filename, thresh)
    
    config_str = '--psm 7 -c tessedit_char_whitelist=0123456789 '
    text = pytesseract.image_to_string(thresh, config=config_str)
    
    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0


def check_home_loot():
    """Reads the total Gold and Elixir and checks if vaults are 90%+ full."""
    print("\n [Storage] Checking Home Village Vaults...")
    
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    home_gold = _extract_home_number(screen, HOME_GOLD_REGION, "debug_home_gold.png")
    home_elixir = _extract_home_number(screen, HOME_ELIXIR_REGION, "debug_home_elixir.png")
    
    # Calculate the fill percentages
    gold_percent = (home_gold / MAX_GOLD) * 100
    elixir_percent = (home_elixir / MAX_ELIXIR) * 100
    
    print(f" [Storage] Current Wealth -> Gold: {home_gold:,} ({gold_percent:.1f}%) | Elixir: {home_elixir:,} ({elixir_percent:.1f}%)")
    
    # --- NEW: The 90% Alert System ---
    needs_upgrade = False
    
    if gold_percent >= 90:
        print(" [Storage] 🚨 ALERT: Gold Storage is 90%+ FULL! Ready to dump into walls.")
        needs_upgrade = True
        
    if elixir_percent >= 90:
        print(" [Storage] 🚨 ALERT: Elixir Storage is 90%+ FULL! Ready to dump into walls.")
        needs_upgrade = True
        
    # We return needs_upgrade so the main script knows whether to run the Builder!
    return home_gold, home_elixir, needs_upgrade

# ... (keep generate_home_calibration and the testing trigger the same) ...

def generate_home_calibration():
    print(" [Storage] Generating calibration image...")
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    
    gy1, gy2, gx1, gx2 = HOME_GOLD_REGION
    cv2.rectangle(screen, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2) 
    
    ey1, ey2, ex1, ex2 = HOME_ELIXIR_REGION
    cv2.rectangle(screen, (ex1, ey1), (ex2, ey2), (255, 0, 255), 2) 
    
    cv2.imwrite("home_calibration.png", screen)
    print(" [Storage] 'home_calibration.png' saved! Check your boxes.")

if __name__ == "__main__":
    generate_home_calibration()
    check_home_loot()