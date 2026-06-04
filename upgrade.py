import cv2
import numpy as np
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

# =========================================================
# LIVE COORDINATES
# =========================================================
BUILDER_X = 750  
BUILDER_Y = 60   
FIXED_TAP_X = 700  
FIXED_TAP_Y = 700  
POINT_A_X = 890  
POINT_A_Y = 700  
POINT_B_X = 960  
POINT_B_Y = 580  

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

# Added the half-swipe function
def scroll_half_down_builder_menu(region):
    print(" [Scroll] Performing half-scroll lookahead...")
    y1, y2, x1, x2 = region
    start_x = (x1 + x2) // 2
    start_y = int(y2 * 0.75)
    end_y = int(y2 * 0.45)
    from config import device
    device.input_swipe(start_x, start_y, start_x, end_y, 400)

def parse_wall_quantity(text_line):
    """Extracts the number after 'Wall', forgiving OCR mistakes on the 'x'."""
    # \D* means "ignore any characters that are NOT numbers" (like ' ', 'x', '*', etc.)
    # \d+ means "capture the first group of numbers you find" (which is the quantity)
    match = re.search(r'wall\D*(\d+)', text_line, flags=re.I)
    
    if match:
        return int(match.group(1))
    return 0  # Default to 0 if OCR misses it entirely to avoid blind tapping
    
def parse_wall_cost(text_line):
    if "wall" not in text_line.lower():
        return None
    text_line = re.sub(r'wall\s*x\d+', '', text_line, flags=re.I)
    text_line = text_line.replace('!', '').replace('@', '').replace('|', '').replace(':', '').replace(';', '')
    matches = re.findall(r'(\d[\d ]+)', text_line)
    if not matches:
        return None
    numbers = []
    for m in matches:
        digits = re.sub(r'\D', '', m)
        if digits:
            numbers.append(int(digits))
    return max(numbers) if numbers else None

# Grouped your exact OCR logic here so we can call it twice (before and after swipe)
def scan_crop_for_walls(crop, x1, y1):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    bigger = cv2.resize(inverted, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    d = pytesseract.image_to_data(bigger, config=r'--psm 6', output_type=Output.DICT)
    
    lines = {}
    for i in range(len(d['text'])):
        text = d['text'][i].strip()
        if not text: continue
        block, line_num = d['block_num'][i], d['line_num'][i]
        line_key = f"{block}_{line_num}"
        if line_key not in lines:
            lines[line_key] = {"words": [], "top": d['top'][i], "bottom": d['top'][i]+d['height'][i], "left": d['left'][i], "right": d['left'][i]+d['width'][i]}
        lines[line_key]["words"].append(text)
        lines[line_key]["top"] = min(lines[line_key]["top"], d['top'][i])
        lines[line_key]["bottom"] = max(lines[line_key]["bottom"], d['top'][i] + d['height'][i])
        lines[line_key]["left"] = min(lines[line_key]["left"], d['left'][i])
        lines[line_key]["right"] = max(lines[line_key]["right"], d['left'][i] + d['width'][i])

    view_walls = []
    for key, line_data in lines.items():
        full_line_text = " ".join(line_data["words"])
        if "wall" in full_line_text.lower():
            cost = parse_wall_cost(full_line_text)
            if cost is not None:
                click_x = x1 + ((line_data["left"] + line_data["right"]) // 2) // 2
                click_y = y1 + ((line_data["top"] + line_data["bottom"]) // 2) // 2
                view_walls.append({"text": full_line_text, "cost": cost, "click_x": click_x, "click_y": click_y})
    
    return view_walls


# --- REMOVED MAX_TAPS PARAMETER FOR TRUE UNCHAINED AUTOMATION ---
def find_and_click_lowest_cost_wall(available_gold, available_elixir, max_scroll_steps=6):
    print("=== STEP 5: Finding & Clicking Lowest Cost Wall (Smart Scan) ===")
    print(f" [Budget] Live Gold: {available_gold:,} | Live Elixir: {available_elixir:,}")
    
    click_coordinates(BUILDER_X, BUILDER_Y)
    time.sleep(0.8) 
    
    for current_step in range(max_scroll_steps + 1):
        print(f"\n--- Scanning Menu Layer {current_step + 1}/{max_scroll_steps + 1} ---")
        
        scrolled_screen = get_current_screen()
        y1, y2, x1, x2 = BUILDER_LIST_REGION
        crop = scrolled_screen[y1:y2, x1:x2]
        
        if crop.size == 0:
            print(" [Error] Crop failed.")
            return

        # 1. Read the screen using your logic
        current_view_walls = scan_crop_for_walls(crop, x1, y1)

        # 2. If a wall is found, half-swipe and read AGAIN
        if current_view_walls:
            print(" [Found] Wall detected! Performing half-swipe to check for better options...")
            scroll_half_down_builder_menu(BUILDER_LIST_REGION)
            time.sleep(0.8)
            
            # Get fresh screenshot and crop after the swipe
            new_screen = get_current_screen()
            new_crop = new_screen[y1:y2, x1:x2]
            
            # Read the new screen using your exact logic
            final_view_walls = scan_crop_for_walls(new_crop, x1, y1)
            
            # Safety fallback in case the swipe messed up the view
            if not final_view_walls:
                final_view_walls = current_view_walls
        else:
            final_view_walls = []

        # 3. Your original calculation and clicking logic
        if final_view_walls:
            lowest_wall = min(final_view_walls, key=lambda x: x["cost"])
            wall_cost = lowest_wall["cost"]
            raw_text = lowest_wall["text"]
            
            print(f"\n [Found] Target Wall Cost: {wall_cost:,}")
            
            # 1. Parse how many walls physically exist
            physical_walls_available = parse_wall_quantity(raw_text)
            
            # 2. Calculate how many upgrades your gold/elixir can afford
            max_gold_upgrades = available_gold // wall_cost
            max_elixir_upgrades = available_elixir // wall_cost
            financial_affordable_walls = max(max_gold_upgrades, max_elixir_upgrades)
            
            # =========================================================
            # DYNAMIC UNCACHED DECISION LOGIC
            # =========================================================
            # Picks the absolute lower value between physical capacity and bank capacity
            actual_taps = min(financial_affordable_walls, physical_walls_available)
            
            print(f" ⭐ [Analysis] Budget can afford: {financial_affordable_walls} | Village has: {physical_walls_available}")
            print(f" ⭐ [Decision] Bot has automatically set tap run sequence to: {actual_taps} taps.")
            
            if actual_taps == 0:
                print(" [!] Safety Abort: 0 upgrades possible. Closing out.")
                break
            
            # Target row select
            click_coordinates(lowest_wall["click_x"], lowest_wall["click_y"])
            time.sleep(1.2)  
            
            # Run dynamic loops completely based on Bot decision
            print(f" [Action] Firing {actual_taps} consecutive clicks on upgrade button...")
            for i in range(actual_taps):
                click_coordinates(FIXED_TAP_X, FIXED_TAP_Y)
                print(f"   -> Tap {i+1}/{actual_taps} fired successfully")
                time.sleep(0.25)
            
            time.sleep(0.8)  
            
            # Post-Upgrade Sequence
            print("\n--- RUNNING POST-UPGRADE SEQUENTIAL TAPS ---")
            click_coordinates(POINT_A_X, POINT_A_Y)
            time.sleep(1.0)
            click_coordinates(POINT_B_X, POINT_B_Y)
            time.sleep(0.5)
            
            print(" [Success] Dynamic safe wall loop complete!")
            return 

        if current_step < max_scroll_steps:
            print(" [Info] No walls on this layer. Scrolling down...")
            scroll_down_builder_menu(BUILDER_LIST_REGION, loops=1)
            time.sleep(0.6)

    print("\n [!] Exiting: Menu closed or sequence completed.")
    find_and_click("empty_grass.png", click=True)

# Removed hardcoded fake numbers from test loop execution 
if __name__ == "__main__":
    print(" [Info] Script ready. Call check_storage.py to execute loop with live parameters.")