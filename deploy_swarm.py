import time
import random
import cv2  
import os
import json 
from config import find_and_click, device, add_log, DEBUG_MODE

def deploy_swarm(troop_name, category, bunches, all_side_points, panic_points, chosen_side_name):
    total_dropping = sum(bunches)
    end_image = f"end_{troop_name}.png"
    
    # =================================================================
    # --- CHECK CONFIG.JSON FOR DEPLOYMENT STRATEGY ---
    # =================================================================
    deploy_strategy = "single_side"
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config_data = json.load(f)
                deploy_strategy = config_data.get("deploy_strategy", "single_side")
    except Exception as e:
        print(" [!] Could not read config.json, defaulting to single_side.")

    if deploy_strategy == "all_sides":
        print(f" [Deploy] Executing SURROUND attack on ALL sides randomly...")
        safe_points = []
        for side_points in all_side_points.values():
            safe_points.extend(side_points)
        random.shuffle(safe_points) 
    else:
        if chosen_side_name not in all_side_points:
            chosen_side_name = random.choice(list(all_side_points.keys()))
        safe_points = all_side_points[chosen_side_name] 
        print(f" [Deploy] Executing on vector {chosen_side_name}...")

    # =================================================================
    # --- SPELL CALCULATION & DEBUG MAP ---
    # =================================================================
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
            drop_x = base_x 
            drop_y = base_y

        final_drop_coords.append((drop_x, drop_y))

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

    # =================================================================
    # --- DEPLOYMENT EXECUTION ---
    # =================================================================
    if category == "spell":
        spell_commands = []
        for i in range(len(bunches)):
            if final_drop_coords[i]:
                dx, dy = final_drop_coords[i]
                spell_commands.append(f"input tap {dx} {dy}")
        if spell_commands:
            device.shell(" && sleep 0.01 && ".join(spell_commands))
        print(f" [Deploy] SUCCESS: {troop_name} spells deep-striked.")
        return True

    i = 0
    while i < len(bunches):
        troops_to_drop = bunches[i]
        if troops_to_drop <= 0:
            i += 1
            continue
            
        if category == "hero":
            tap_count = random.randint(2, 3)
            tap_commands = []
            for _ in range(tap_count):
                random_pt = random.choice(safe_points)
                hx = random_pt[0] + random.randint(-15, 15)
                hy = random_pt[1] + random.randint(-15, 15)
                tap_commands.append(f"input tap {hx} {hy}")
            device.shell(" && sleep 0.01 && ".join(tap_commands))
            i += 1
            continue
            
        if category == "troop":
            troops_remaining = troops_to_drop
            commands = []
            point_idx = random.randint(0, len(safe_points) - 1)
            
            while troops_remaining > 0:
                # ✅ Grab as many as possible per hold — bigger chunk = longer hold = more troops deployed
                chunk = min(random.randint(30, 50), troops_remaining)
                troops_remaining -= chunk
                
                base_pt = safe_points[point_idx % len(safe_points)]
                point_idx += 1 

                hx = base_pt[0] + random.randint(-15, 15)
                hy = base_pt[1] + random.randint(-15, 15)
                
                # ✅ CORE FIX: hold_time is now purely based on chunk size
                # ~40ms per troop — holding longer = game deploys more units continuously
                # For 50 troops: ~2000ms hold. For 30 troops: ~1200ms hold.
                hold_time = chunk * 40  # tweak this multiplier (30–50) to match your game's spawn rate
                
                commands.append(f"input swipe {hx} {hy} {hx} {hy} {hold_time}")
            
            # ✅ No sleep between commands — fire them back to back instantly
            device.shell(" && ".join(commands))
                
        i += 1 

    # Cleanup taps — batched, no sleep
    cleanup_commands = []
    for extra in range(2):
        cleanup_pt = random.choice(safe_points)
        cleanup_commands.append(f"input tap {cleanup_pt[0]} {cleanup_pt[1]}")
    device.shell(" && ".join(cleanup_commands))

    # --- FAST VERIFICATION (TROOPS ONLY) ---
    if category == "troop":
        time.sleep(0.1)
        end_img_path = os.path.join("assets", end_image)
        if not os.path.exists(end_img_path):
            print(f"   [!] Skipping verification: '{end_image}' missing.")
        else:
            for retry in range(2): 
                if find_and_click(end_image, click=False, threshold=0.85):
                    print(f" [Deploy] SUCCESS: Verified all {troop_name}s.")
                    return True
                
                panic_pt = random.choice(panic_points)
                device.shell(f"input swipe {panic_pt[0]} {panic_pt[1]} {panic_pt[0]} {panic_pt[1]} 80")
                time.sleep(0.05)

    print(f" [Deploy] SUCCESS: {troop_name}s deployed.")
    return True