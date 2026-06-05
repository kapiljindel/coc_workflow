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

# Split upgrade buttons for Gold and Elixir
GOLD_UPGRADE_X = 890   # Old POINT_A coordinates used for Gold
GOLD_UPGRADE_Y = 700   
ELIXIR_UPGRADE_X = 1050 # Change these coordinates if your Elixir button is elsewhere!
ELIXIR_UPGRADE_Y = 680 # Adjust to match your Elixir button location

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

def scroll_half_down_builder_menu(region):
    print(" [Scroll] Performing half-scroll lookahead...")
    y1, y2, x1, x2 = region
    start_x = (x1 + x2) // 2
    start_y = int(y2 * 0.75)
    end_y = int(y2 * 0.45)
    from config import device
    device.input_swipe(start_x, start_y, start_x, end_y, 400)

def parse_wall_quantity(text_line):
    match = re.search(r'wall\D*(\d+)', text_line, flags=re.I)
    if match:
        return int(match.group(1))
    return 0 
    
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

        current_view_walls = scan_crop_for_walls(crop, x1, y1)

        if current_view_walls:
            print(" [Found] Wall detected! Performing half-swipe to check for better options...")
            scroll_half_down_builder_menu(BUILDER_LIST_REGION)
            time.sleep(0.8)
            
            new_screen = get_current_screen()
            new_crop = new_screen[y1:y2, x1:x2]
            
            final_view_walls = scan_crop_for_walls(new_crop, x1, y1)
            
            if not final_view_walls:
                final_view_walls = current_view_walls
        else:
            final_view_walls = []

        if final_view_walls:
            lowest_wall = min(final_view_walls, key=lambda x: x["cost"])
            wall_cost = lowest_wall["cost"]
            raw_text = lowest_wall["text"]
            
            print(f"\n [Found] Target Wall Cost: {wall_cost:,}")
            
            physical_walls_available = parse_wall_quantity(raw_text)
            
            # Target row select
            click_coordinates(lowest_wall["click_x"], lowest_wall["click_y"])
            time.sleep(1.2)  
            
            # =========================================================
            # TWO-PASS UPGRADE LOGIC (GOLD THEN ELIXIR)
            # =========================================================
            remaining_walls = physical_walls_available
            
            # Pass 1: Gold Upgrades
            gold_taps = min(available_gold // wall_cost, remaining_walls)
            if gold_taps > 0:
                print(f" [Action] Firing {gold_taps} clicks for Gold upgrade...")
                for i in range(gold_taps):
                    click_coordinates(FIXED_TAP_X, FIXED_TAP_Y)
                    time.sleep(0.25)
                
                time.sleep(0.8)  
                print("--- RUNNING GOLD POST-UPGRADE SEQUENTIAL TAPS ---")
                click_coordinates(GOLD_UPGRADE_X, GOLD_UPGRADE_Y)
                time.sleep(1.0)
                remaining_walls -= gold_taps
            else:
                print(" [Info] Skipping Gold upgrade (insufficient gold or no walls).")

            # Pass 2: Elixir Upgrades
            elixir_taps = min(available_elixir // wall_cost, remaining_walls)
            if elixir_taps > 0:
                print(f" [Action] Firing {elixir_taps} clicks for Elixir upgrade...")
                for i in range(elixir_taps):
                    click_coordinates(FIXED_TAP_X, FIXED_TAP_Y)
                    time.sleep(0.25)
                
                time.sleep(0.8)  
                print("--- RUNNING ELIXIR POST-UPGRADE SEQUENTIAL TAPS ---")
                click_coordinates(ELIXIR_UPGRADE_X, ELIXIR_UPGRADE_Y)
                time.sleep(1.0)
                remaining_walls -= elixir_taps
            else:
                print(" [Info] Skipping Elixir upgrade (insufficient elixir or no walls remaining).")

            # Final close tap (Point B)
            click_coordinates(POINT_B_X, POINT_B_Y)
            time.sleep(0.5)
            
            print(" [Success] Dynamic safe dual-loot wall loop complete!")
            return 

        if current_step < max_scroll_steps:
            print(" [Info] No walls on this layer. Scrolling down...")
            scroll_down_builder_menu(BUILDER_LIST_REGION, loops=1)
            time.sleep(0.6)

    print("\n [!] Exiting: Menu closed or sequence completed.")
    find_and_click("empty_grass.png", click=True)

if __name__ == "__main__":
    print(" [Info] Script ready. Call check_storage.py to execute loop with live parameters.")