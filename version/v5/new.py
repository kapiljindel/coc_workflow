"""
CoC Bot Configuration Module
Handles ADB connection, OCR, image recognition, and core utilities
"""

import cv2
import numpy as np
import os
import sys
import pytesseract
from ppadb.client import Client as AdbClient
import random
import time
from datetime import datetime
from typing import Tuple, Dict, List, Optional

# ===========================================
# CONFIGURATION CONSTANTS
# ===========================================

# ADB Settings
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037
DEVICE_PORT = 5555

# Paths
ASSETS_PATH = "assets"
LOGS_PATH = "logs"
IMG_PATH = "img"

# Tesseract Configuration - Auto-detect or use environment variable
TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')  # Falls back to PATH
if os.path.exists(r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'):
    TESSERACT_CMD = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Loot Thresholds
MINIMUM_GOLD = 600000
MINIMUM_ELIXIR = 600000

# Total Army Space (update based on your Town Hall level)
TOTAL_TROOPS = 320  # Example: TH15 = 320 housing space

# UI Regions (Y1, Y2, X1, X2) - ADJUST THESE FOR YOUR RESOLUTION
GOLD_REGION = (125, 160, 75, 250)
ELIXIR_REGION = (165, 200, 75, 250)
DAMAGE_REGION = (620, 700, 1350, 1580)
TROOP_REGION = (738, 768, 150, 250)

# Home Village Storage Coordinates (Top Right)
HOME_GOLD_REGION = (32, 73, 1300, 1510)
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

# Correct Storage Capacities (adjust for your Town Hall level)
# TH15 example values:
MAX_GOLD = 16000000      # 16 million
MAX_ELIXIR = 16000000    # 16 million

# ===========================================
# ARMY CONFIGURATION
# ===========================================
# This will be populated by army_builder.py or use defaults
MY_ARMY: List[Dict] = [
    {"name": "dragon", "category": "troop", "count": 9},
    {"name": "king", "category": "hero", "count": 1},
    {"name": "queen", "category": "hero", "count": 1},
    {"name": "freeze", "category": "spell", "count": 5},
    {"name": "rage", "category": "spell", "count": 1},
]

ARMY_SLOTS: Dict[str, Tuple[int, int, int, int]] = {}

# ===========================================
# LOGGING SYSTEM
# ===========================================
LOG_BUFFER = {
    "resources": [],
    "attack": [],
    "errors": [],
    "buttons": [],
    "system": []
}


def add_log(category: str, message: str) -> None:
    """Add a log entry with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    if category in LOG_BUFFER:
        LOG_BUFFER[category].append(log_entry)
        print(f" [{category.upper()}] {message}")
    else:
        print(f" [WARNING] Unknown log category: {category}")


def flush_logs() -> None:
    """Save all buffered logs to disk"""
    try:
        if not os.path.exists(LOGS_PATH):
            os.makedirs(LOGS_PATH)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        for category, lines in LOG_BUFFER.items():
            if lines:
                log_file = os.path.join(LOGS_PATH, f"{date_str}_{category}.txt")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
                LOG_BUFFER[category] = []
        
        print(" [System] All logs saved to /logs/ folder.")
    except Exception as e:
        print(f" [ERROR] Failed to flush logs: {e}")


# ===========================================
# ADB CONNECTION
# ===========================================
def connect_to_device(max_retries: int = 3) -> Optional[object]:
    """
    Connect to Android device via ADB with retry logic
    
    Args:
        max_retries: Maximum number of connection attempts
        
    Returns:
        Device object if successful, None otherwise
    """
    for attempt in range(max_retries):
        try:
            print(f" [ADB] Connection attempt {attempt + 1}/{max_retries}...")
            
            client = AdbClient(host=ADB_HOST, port=ADB_PORT)
            
            # Try to connect remotely
            try:
                client.remote_connect(ADB_HOST, DEVICE_PORT)
            except Exception as e:
                print(f" [ADB] Remote connect failed (may already be connected): {e}")
            
            # Get device
            device = client.device(f"{ADB_HOST}:{DEVICE_PORT}")
            
            if device:
                print(f" [ADB] ✓ Connected to {ADB_HOST}:{DEVICE_PORT}")
                add_log("system", f"ADB Connected to {ADB_HOST}:{DEVICE_PORT}")
                return device
            else:
                print(f" [ADB] No device found at {ADB_HOST}:{DEVICE_PORT}")
                
        except Exception as e:
            print(f" [ADB] Connection error: {e}")
        
        if attempt < max_retries - 1:
            print(" [ADB] Retrying in 3 seconds...")
            time.sleep(3)
    
    print("\n" + "="*60)
    print(" [ERROR] Failed to connect to Android device!")
    print(" ")
    print(" Troubleshooting steps:")
    print(" 1. Make sure BlueStacks/Emulator is running")
    print(" 2. Check ADB is installed and in PATH")
    print(f" 3. Run: adb connect {ADB_HOST}:{DEVICE_PORT}")
    print(" 4. Run: adb devices (should show device)")
    print("="*60 + "\n")
    
    return None


# Initialize device connection
device = connect_to_device()
if not device:
    print(" [FATAL] Cannot continue without device connection. Exiting...")
    sys.exit(1)


# ===========================================
# ARMY SLOT GENERATION
# ===========================================
def generate_army_slots() -> Dict[str, Tuple[int, int, int, int]]:
    """
    Mathematically calculates the exact pixel boxes for the army bar.
    
    Returns:
        Dictionary mapping slot names to (y1, y2, x1, x2) coordinates
    """
    slots = {}
    y1, y2 = 745, 883
    current_x = 123  # Starting X of the first card
    box_width = 112  # Width of a CoC card
    
    for i, unit in enumerate(MY_ARMY):
        slot_name = f"slot_{i+1}"
        unit["slot"] = slot_name  # Inject the slot name into the army list
        
        x1 = int(current_x)
        x2 = int(current_x + box_width)
        slots[slot_name] = (y1, y2, x1, x2)
        
        # Calculate the physical gap for the NEXT card
        if i < len(MY_ARMY) - 1:
            curr_cat = unit["category"]
            next_cat = MY_ARMY[i+1]["category"]
            
            if curr_cat == next_cat:
                current_x = x2 + 10  # Small gap for same type
            else:
                current_x = x2 + 26  # Large gap for new type
    
    return slots


def validate_army_configuration() -> bool:
    """
    Validate that army configuration is valid
    
    Returns:
        True if valid, False otherwise
    """
    if not MY_ARMY:
        add_log("errors", "Army configuration is empty!")
        return False
    
    for unit in MY_ARMY:
        if "name" not in unit or "category" not in unit or "count" not in unit:
            add_log("errors", f"Invalid unit configuration: {unit}")
            return False
        
        if unit["category"] not in ["troop", "hero", "spell"]:
            add_log("errors", f"Invalid category '{unit['category']}' for {unit['name']}")
            return False
        
        if unit["count"] <= 0:
            add_log("errors", f"Invalid count {unit['count']} for {unit['name']}")
            return False
    
    return True


# Generate army slots on module load
if validate_army_configuration():
    ARMY_SLOTS = generate_army_slots()
    add_log("system", f"Army slots generated: {len(ARMY_SLOTS)} units")
else:
    print(" [WARNING] Army configuration validation failed!")


# ===========================================
# IMAGE RECOGNITION & CLICKING
# ===========================================
def find_and_click(image_name: str, threshold: float = 0.8, click: bool = True) -> bool:
    """
    Find an image on screen using template matching and optionally click it
    
    Args:
        image_name: Filename of the template image in assets folder
        threshold: Matching confidence threshold (0.0 to 1.0)
        click: Whether to click the found image
        
    Returns:
        True if image found, False otherwise
    """
    try:
        # Get screenshot
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        
        # Load template
        template_path = os.path.join(ASSETS_PATH, image_name)
        
        if not os.path.exists(template_path):
            add_log("errors", f"Template image not found: {template_path}")
            return False
        
        template = cv2.imread(template_path)
        if template is None:
            add_log("errors", f"Failed to load template: {template_path}")
            return False
        
        # Template matching
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            if click:
                h, w = template.shape[:-1]
                
                # Add random offset for human-like clicking
                margin_x = max(1, int(w * 0.15))
                margin_y = max(1, int(h * 0.15))
                
                random_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
                random_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
                
                # Human-like delay before clicking
                time.sleep(random.uniform(0.15, 0.45))
                
                device.shell(f"input tap {random_x} {random_y}")
                add_log("buttons", f"Clicked {image_name} at ({random_x}, {random_y}) [confidence: {max_val:.2f}]")
            
            return True
        
        return False
        
    except Exception as e:
        add_log("errors", f"find_and_click error for {image_name}: {e}")
        return False


# ===========================================
# OCR NUMBER EXTRACTION
# ===========================================
def _extract_number(screen: np.ndarray, region: Tuple[int, int, int, int], 
                   debug_filename: str, psm_mode: int = 7) -> int:
    """
    Extract a number from a screen region using OCR
    
    Args:
        screen: Screenshot image
        region: (y1, y2, x1, x2) coordinates
        debug_filename: Path to save debug image
        psm_mode: Tesseract page segmentation mode
        
    Returns:
        Extracted number or 0 if extraction fails
    """
    try:
        y1, y2, x1, x2 = region
        
        # Validate region
        h, w = screen.shape[:2]
        if y1 < 0 or y2 > h or x1 < 0 or x2 > w or y1 >= y2 or x1 >= x2:
            add_log("errors", f"Invalid region coordinates: {region}")
            return 0
        
        crop = screen[y1:y2, x1:x2]
        
        if crop.size == 0:
            add_log("errors", f"Empty crop for region {region}")
            return 0
        
        # Upscale for better OCR
        bigger = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Convert to grayscale
        gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
        
        # Threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Save debug image
        if not os.path.exists(IMG_PATH):
            os.makedirs(IMG_PATH)
        cv2.imwrite(debug_filename, thresh)
        
        # OCR configuration
        config_str = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789% '
        
        # Extract text
        text = pytesseract.image_to_string(thresh, config=config_str)
        
        # Clean and convert
        clean_text = ''.join(filter(str.isdigit, text))
        
        return int(clean_text) if clean_text != "" else 0
        
    except Exception as e:
        add_log("errors", f"OCR extraction error: {e}")
        return 0


def read_troops() -> int:
    """Read current troop count from screen"""
    try:
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        return _extract_number(screen, TROOP_REGION, os.path.join(IMG_PATH, "debug_troops.png"))
    except Exception as e:
        add_log("errors", f"read_troops error: {e}")
        return 0


def read_loot() -> Tuple[int, int]:
    """
    Read available loot (gold and elixir) from screen
    
    Returns:
        Tuple of (gold, elixir)
    """
    try:
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        
        gold = _extract_number(screen, GOLD_REGION, os.path.join(IMG_PATH, "debug_gold.png"))
        elixir = _extract_number(screen, ELIXIR_REGION, os.path.join(IMG_PATH, "debug_elixir.png"))
        
        return gold, elixir
    except Exception as e:
        add_log("errors", f"read_loot error: {e}")
        return 0, 0


def read_damage() -> int:
    """Read current destruction percentage from screen"""
    try:
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        return _extract_number(screen, DAMAGE_REGION, os.path.join(IMG_PATH, "debug_damage.png"))
    except Exception as e:
        add_log("errors", f"read_damage error: {e}")
        return 0


# ===========================================
# DEBUG & CALIBRATION
# ===========================================
def save_debug_screenshot() -> None:
    """Save annotated screenshot showing all UI regions"""
    try:
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        
        # Draw loot regions
        cv2.rectangle(screen, (GOLD_REGION[2], GOLD_REGION[0]), 
                     (GOLD_REGION[3], GOLD_REGION[1]), (0, 0, 255), 2)
        cv2.putText(screen, "GOLD", (GOLD_REGION[2], GOLD_REGION[0] - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        cv2.rectangle(screen, (ELIXIR_REGION[2], ELIXIR_REGION[0]),
                     (ELIXIR_REGION[3], ELIXIR_REGION[1]), (255, 0, 255), 2)
        cv2.putText(screen, "ELIXIR", (ELIXIR_REGION[2], ELIXIR_REGION[0] - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # Draw damage region
        cv2.rectangle(screen, (DAMAGE_REGION[2], DAMAGE_REGION[0]),
                     (DAMAGE_REGION[3], DAMAGE_REGION[1]), (0, 255, 0), 2)
        cv2.putText(screen, "DAMAGE", (DAMAGE_REGION[2], DAMAGE_REGION[0] - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw army slots
        for slot_name, coords in ARMY_SLOTS.items():
            sy1, sy2, sx1, sx2 = coords
            cv2.rectangle(screen, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
            cv2.putText(screen, slot_name, (sx1, sy1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        if not os.path.exists(IMG_PATH):
            os.makedirs(IMG_PATH)
        
        output_path = os.path.join(IMG_PATH, "ui_boxes.png")
        cv2.imwrite(output_path, screen)
        print(f" [+] UI Calibration screenshot saved as '{output_path}'!")
        
    except Exception as e:
        add_log("errors", f"save_debug_screenshot error: {e}")


def validate_regions() -> bool:
    """
    Validate that all UI regions are properly configured
    
    Returns:
        True if all regions are valid
    """
    try:
        screen_bytes = device.screencap()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        h, w = screen.shape[:2]
        
        regions = {
            "GOLD_REGION": GOLD_REGION,
            "ELIXIR_REGION": ELIXIR_REGION,
            "DAMAGE_REGION": DAMAGE_REGION,
            "TROOP_REGION": TROOP_REGION,
            "HOME_GOLD_REGION": HOME_GOLD_REGION,
            "HOME_ELIXIR_REGION": HOME_ELIXIR_REGION
        }
        
        all_valid = True
        
        for name, region in regions.items():
            y1, y2, x1, x2 = region
            
            if y1 < 0 or y2 > h or x1 < 0 or x2 > w:
                print(f" [WARNING] {name} is outside screen bounds!")
                all_valid = False
            
            if y1 >= y2 or x1 >= x2:
                print(f" [WARNING] {name} has invalid coordinates!")
                all_valid = False
        
        if all_valid:
            print(" [✓] All UI regions validated successfully!")
        
        return all_valid
        
    except Exception as e:
        add_log("errors", f"validate_regions error: {e}")
        return False


# Validate configuration on module load
if __name__ != "__main__":
    validate_regions()


print(" [Config] Module loaded successfully!")
print(f" [Config] Device: {device}")
print(f" [Config] Army Units: {len(MY_ARMY)}")
print(f" [Config] Army Slots: {len(ARMY_SLOTS)}")