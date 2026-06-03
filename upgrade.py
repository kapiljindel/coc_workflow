import cv2
import pytesseract
from pytesseract import Output
import os
import time
import re
from config import (
    click_coordinates, 
    get_current_screen,
    BUILDER_LIST_REGION, 
    find_and_click,
    scroll_down_builder_menu
)

# 1. Main Menu Navigation Coordinates
BUILDER_X = 750  
BUILDER_Y = 60   

# 2. Fixed Upgrade Button Coordinates
FIXED_TAP_X = 700  
FIXED_TAP_Y = 700  

# 3. NEW: Next Two Sequential Points (Change these to your exact pixel coordinates)
POINT_A_X = 890  # Replace with your first follow-up point X
POINT_A_Y = 700  # Replace with your first follow-up point Y

# 4. NEW: Second Follow-Up Point
POINT_B_X = 960  # Replace with your second follow-up point X
POINT_B_Y = 580  # Replace with your second follow-up point Y


# Your custom OCR error correction dictionary
SIMILAR_CHARS = {
    "0": ["O", "o", "°", "○", "●"],
    "1": ["!", "|", "I", "l", "L", "i"],
    "2": ["Z", "z"],
    "3": ["E"],
    "4": ["A", "@"],
    "5": ["S", "s", "$"],
    "6": ["G", "g"],
    "7": ["T", "t", "+"],
    "8": ["B", "b", "&"],
    "9": ["q", "Q", "g"],
}

def parse_wall_cost(text_line):
    if "wall" not in text_line.lower():
        return None

    # Remove wall quantity first
    text_line = re.sub(r'wall\s*x\d+', '', text_line, flags=re.I)

    # Common OCR mistakes
    text_line = text_line.replace('!', '')
    text_line = text_line.replace('@', '')
    text_line = text_line.replace('|', '')
    text_line = text_line.replace(':', '')
    text_line = text_line.replace(';', '')

    # Find groups of numbers
    matches = re.findall(r'(\d[\d ]+)', text_line)

    if not matches:
        return None

    numbers = []
    for m in matches:
        digits = re.sub(r'\D', '', m)
        if digits:
            numbers.append(int(digits))

    if not numbers:
        return None

    return max(numbers)

def find_and_click_lowest_cost_wall(taps=2):
    print("=== STEP 5: Finding & Clicking Lowest Cost Wall ===")
    
    # 1. Drop down the menu and slide it to the absolute bottom
    click_coordinates(BUILDER_X, BUILDER_Y)
    time.sleep(0.8) 
    scroll_down_builder_menu(BUILDER_LIST_REGION, loops=10)
    time.sleep(0.5)
    
    # 2. Capture screen and crop down directly to your blue box
    scrolled_screen = get_current_screen()
    y1, y2, x1, x2 = BUILDER_LIST_REGION
    crop = scrolled_screen[y1:y2, x1:x2]
    
    if crop.size == 0:
        print(" [Error] Blue box region crop failed.")
        return

    # 3. Clean image for OCR
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    bigger = cv2.resize(inverted, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 4. Use image_to_data to read text AND track precise pixel coordinates
    custom_config = r'--psm 6'
    d = pytesseract.image_to_data(bigger, config=custom_config, output_type=Output.DICT)
    
    # Reconstruct bounding boxes for each row line dynamically
    lines = {}
    for i in range(len(d['text'])):
        text = d['text'][i].strip()
        if not text:
            continue
            
        block = d['block_num'][i]
        line_num = d['line_num'][i]
        line_key = f"{block}_{line_num}"
        
        if line_key not in lines:
            lines[line_key] = {
                "words": [],
                "top": d['top'][i],
                "bottom": d['top'][i] + d['height'][i],
                "left": d['left'][i],
                "right": d['left'][i] + d['width'][i]
            }
            
        lines[line_key]["words"].append(text)
        lines[line_key]["top"] = min(lines[line_key]["top"], d['top'][i])
        lines[line_key]["bottom"] = max(lines[line_key]["bottom"], d['top'][i] + d['height'][i])
        lines[line_key]["left"] = min(lines[line_key]["left"], d['left'][i])
        lines[line_key]["right"] = max(lines[line_key]["right"], d['left'][i] + d['width'][i])

    # 5. Process data to find the lowest individual wall cost
    lowest_cost = float('inf')
    target_line_coords = None
    target_text = ""
    
    print("\n--- CLEANED WALL TRANSLATIONS ---")
    for key, line_data in lines.items():
        full_line_text = " ".join(line_data["words"])
        
        if "wall" in full_line_text.lower():
            cost = parse_wall_cost(full_line_text)
            if cost is not None:
                print(f" [+] Row parsed: '{full_line_text}' -> Individual Cost: {cost:,}")
                if cost < lowest_cost:
                    lowest_cost = cost
                    target_line_coords = line_data
                    target_text = full_line_text
            else:
                print(f" [!] Skipping unparseable row: '{full_line_text}'")

    # 6. Click the exact row coordinates, then execute dynamic taps
    if target_line_coords and lowest_cost != float('inf'):
        processed_center_y = (target_line_coords["top"] + target_line_coords["bottom"]) // 2
        processed_center_x = (target_line_coords["left"] + target_line_coords["right"]) // 2
        
        crop_center_y = processed_center_y // 2
        crop_center_x = processed_center_x // 2
        
        click_x = x1 + crop_center_x
        click_y = y1 + crop_center_y
        
        print(f"\n [Decision] Lowest cost option is '{target_text}' ({lowest_cost:,})")
        print(f" [Action] Tapping text target directly at: ({click_x}, {click_y})")
        
        # Click the row item to select the wall on map
        click_coordinates(click_x, click_y)
        time.sleep(1.2)  # Pause for camera adjustment
        
        # Execute the main upgrade taps
        print(f" [Action] Executing {taps} taps on upgrade button at: ({FIXED_TAP_X}, {FIXED_TAP_Y})")
        for i in range(taps):
            click_coordinates(FIXED_TAP_X, FIXED_TAP_Y)
            print(f"   -> Tap {i+1}/{taps} fired")
            time.sleep(0.25)
        
        time.sleep(0.8)  # Short breather after upgrade finishes
        
        # --- 7. NEW: SEQUENTIAL FOLLOW-UP TAPS ---
        print("\n--- RUNNING POST-UPGRADE SEQUENTIAL TAPS ---")
        
        # Trigger Point A
        print(f" [Action] Triggering Point A at: ({POINT_A_X}, {POINT_A_Y})")
        click_coordinates(POINT_A_X, POINT_A_Y)
        time.sleep(1.0)  # Wait for whatever window/animation Point A triggers
        
        # Trigger Point B
        print(f" [Action] Triggering Point B at: ({POINT_B_X}, {POINT_B_Y})")
        click_coordinates(POINT_B_X, POINT_B_Y)
        time.sleep(0.5)
        
        print(" [Success] Entire wall loop and follow-up sequence complete!")
    else:
        print("\n [!] Target aborted: No upgradeable walls discovered.")
        find_and_click("empty_grass.png", click=True)

if __name__ == "__main__":
    # Change taps=5 to whatever your layout needs!
    find_and_click_lowest_cost_wall(taps=5)