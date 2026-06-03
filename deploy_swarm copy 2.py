import time
import random
import cv2  
import os
from config import find_and_click, device, add_log, DEBUG_MODE

def deploy_swarm(troop_name, category, bunches, all_side_points, panic_points, chosen_side_name):
    total_dropping = sum(bunches)
    end_image = f"end_{troop_name}.png"
    
    if chosen_side_name not in all_side_points:
        chosen_side_name = random.choice(list(all_side_points.keys()))
        
    safe_points = all_side_points[chosen_side_name] 
    
    print(f" [Deploy] Executing on vector {chosen_side_name}...")
    
    step = max(1, len(safe_points) / max(1, len(bunches)))
    final_drop_coords = []
    
    all_x = [pt[0] for side in all_side_points.values() for pt in side]
    all_y = [pt[1] for side in all_side_points.values() for pt in side]
    center_x = sum(all_x) / max(1, len(all_x))
    center_y = sum(all_y) / max(1, len(all_y))
    
    for i in range(len(bunches)):
        if bunches[i] <= 0:
            final_drop_coords.append(None)
            continue
            
        pt_index = min(int(i * step), len(safe_points) - 1)
        base_x, base_y = safe_points[pt_index]
        
        if category == "spell":
            penetration = random.uniform(0.55, 0.75)
            drop_x = int(base_x + (center_x - base_x) * penetration)
            drop_y = int(base_y + (center_y - base_y) * penetration)
            drop_x += random.randint(-40, 40)
            drop_y += random.randint(-40, 40)
        else:
            drop_x = base_x + random.randint(-3, 3)
            drop_y = base_y + random.randint(-3, 3)

        final_drop_coords.append((drop_x, drop_y))

    # Only save tactical map points if debug mode is on
    if DEBUG_MODE:
        try:
            if os.path.exists("img/tactical_map.png"):
                calib_img = cv2.imread("img/tactical_map.png")
                if calib_img is not None:
                    for coord in final_drop_coords:
                        if coord is not None:
                            dot_color = (255, 0, 255) if category == "spell" else (0, 255, 255)
                            cv2.circle(calib_img, coord, 8, dot_color, -1)
                            cv2.circle(calib_img, coord, 8, (0, 0, 0), 2)
                    cv2.imwrite("img/tactical_map.png", calib_img)
        except Exception as e:
            pass

    # --- CATEGORY: SPELLS ---
    if category == "spell":
        for i in range(len(bunches)):
            if final_drop_coords[i]:
                dx, dy = final_drop_coords[i]
                device.shell(f"input tap {dx} {dy}")
                time.sleep(random.uniform(0.02, 0.08)) 
        print(f" [Deploy] SUCCESS: {troop_name} spells deep-striked.")
        return True

    # --- CATEGORY: HEROES & TROOPS ---
    i = 0
    while i < len(bunches):
        troops_to_drop = bunches[i]
        if troops_to_drop <= 0:
            i += 1
            continue
            
        # --- FIXED: TRUE LIGHTNING ADB BATCH TAPS ---
        if category == "hero":
            tap_count = random.randint(2, 3)
            tap_commands = []
            for _ in range(tap_count):
                random_pt = random.choice(safe_points)
                hx = random_pt[0] + random.randint(-15, 15)
                hy = random_pt[1] + random.randint(-15, 15)
                tap_commands.append(f"input tap {hx} {hy}")
                
            # Send all taps in one single ultra-fast ADB shell session
            device.shell(" && sleep 0.05 && ".join(tap_commands))
            i += 1
            continue
            
        drop_x, drop_y = final_drop_coords[i]
        hold_time = random.randint(40, 80) + (troops_to_drop * random.randint(15, 25))
        end_x = drop_x + random.randint(-5, 5)
        end_y = drop_y + random.randint(-5, 5)
        
        device.shell(f"input swipe {drop_x} {drop_y} {end_x} {end_y} {hold_time}")
        time.sleep(random.uniform(0.02, 0.06)) 
            
        i += 1 

    # Clean-up taps
    for extra in range(2):
        cleanup_pt = random.choice(safe_points)
        device.shell(f"input tap {cleanup_pt[0]} {cleanup_pt[1]}")
        time.sleep(random.uniform(0.01, 0.04))

    # --- FAST VERIFICATION (TROOPS ONLY) ---
    if category == "troop":
        time.sleep(random.uniform(0.15, 0.35))
        end_img_path = os.path.join("assets", end_image)
        if not os.path.exists(end_img_path):
            print(f"   [!] Skipping verification: '{end_image}' missing.")
        else:
            for retry in range(2): 
                if find_and_click(end_image, click=False, threshold=0.85):
                    print(f" [Deploy] SUCCESS: Verified all {troop_name}s.")
                    return True
                
                panic_pt = random.choice(panic_points)
                device.shell(f"input swipe {panic_pt[0]} {panic_pt[1]} {panic_pt[0]} {panic_pt[1]} 200")
                time.sleep(random.uniform(0.08, 0.15))

    print(f" [Deploy] SUCCESS: {troop_name}s deployed.")
    return True