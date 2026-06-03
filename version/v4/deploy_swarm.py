import time
import random
import cv2  
import os
from config import find_and_click, device, add_log

def deploy_swarm(troop_name, bunches, all_side_points, panic_points):
    end_image = f"end_{troop_name}.png"
    total_dropping = sum(bunches)
    
    valid_sides = {k: v for k, v in all_side_points.items() if len(v) >= len(bunches)}
    if not valid_sides:
        print(" [Deploy] ERROR: Base is too restricted! Defaulting to Panic Mode.")
        return False
        
    chosen_side_name = random.choice(list(valid_sides.keys()))
    safe_points = valid_sides[chosen_side_name] 
    
    print(f" [Deploy] Locked onto {chosen_side_name}. Spreading {total_dropping} {troop_name}s...")
    add_log("attack", f"Dropping {total_dropping} {troop_name}s on {chosen_side_name}.")
    
    step = len(safe_points) / max(1, len(bunches))
    final_drop_coords = []
    
    for i in range(len(bunches)):
        if bunches[i] <= 0:
            final_drop_coords.append(None)
            continue
            
        pt_index = min(int(i * step), len(safe_points) - 1)
        base_x, base_y = safe_points[pt_index]
        
        drop_x = base_x + random.randint(-3, 3)
        drop_y = base_y + random.randint(-3, 3)
        final_drop_coords.append((drop_x, drop_y))

    # PRE-DRAW EXACT DROPS ON THE TACTICAL MAP
    try:
        if os.path.exists("img/tactical_map.png"):
            calib_img = cv2.imread("img/tactical_map.png")
            if calib_img is not None:
                for coord in final_drop_coords:
                    if coord is not None:
                        cv2.circle(calib_img, coord, 8, (0, 255, 255), -1)
                        cv2.circle(calib_img, coord, 8, (0, 0, 0), 2)
                cv2.imwrite("img/tactical_map.png", calib_img)
    except Exception as e:
        print(f" [Deploy] Warning: Could not update tactical map: {e}")

    # MAIN DEPLOYMENT LOOP
    i = 0
    while i < len(bunches):
        troops_to_drop = bunches[i]
        if troops_to_drop <= 0:
            i += 1
            continue
            
        drop_x, drop_y = final_drop_coords[i]
        hold_time = random.randint(120, 180) + (troops_to_drop * random.randint(70, 95))
        end_x = drop_x + random.randint(-3, 3)
        end_y = drop_y + random.randint(-3, 3)
        
        device.shell(f"input swipe {drop_x} {drop_y} {end_x} {end_y} {hold_time}")
        time.sleep(random.uniform(0.15, 0.25)) 
        
        if find_and_click("red_area_error.png", click=False, threshold=0.7):
            print("   [!] RED ZONE DETECTED! Skipping point...")
            time.sleep(random.uniform(0.2, 0.4))
            continue 
        else:
            i += 1 
            time.sleep(random.uniform(0.02, 0.08)) 

    # THE 2 EXTRA CLEAN-UP DEPLOYS
    for extra in range(2):
        cleanup_pt = random.choice(safe_points)
        device.shell(f"input swipe {cleanup_pt[0]} {cleanup_pt[1]} {cleanup_pt[0]+2} {cleanup_pt[1]+2} 400")
        time.sleep(0.15)

    # PERSISTENT VERIFICATION
    time.sleep(0.8)
    for retry in range(5):
        if find_and_click(end_image, click=False, threshold=0.85):
            print(f" [Deploy] SUCCESS: All {troop_name}s deployed.")
            return True
        
        print(f" [Deploy] WARNING: {troop_name}s remaining (Try {retry+1}/5). Using UNBREAKABLE PANIC RING.")
        panic_pt = random.choice(panic_points)
        device.shell(f"input swipe {panic_pt[0]} {panic_pt[1]} {panic_pt[0]} {panic_pt[1]} {random.randint(2500, 3500)}")
        time.sleep(0.5) 

    return True