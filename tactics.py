import select_troop
import troop_calculator
import deploy_swarm
import base_scanner
from config import device, add_log
import random  

def execute_full_army_attack(army_composition):
    print("\n=== [Commander] INITIATING FULL ARMY ASSAULT ===")
    
    print(" [Commander] Scanning base geometry...")
    screen_bytes = device.screencap()
    all_side_points, panic_points = base_scanner.get_safe_spam_points(screen_bytes)
    
    if not all_side_points:
        print(" [Commander] FATAL ERROR: Base scan failed.")
        return False

    chosen_side_name = random.choice(list(all_side_points.keys()))
    print(f" [Commander] Master Tactical Vector Locked: {chosen_side_name}")

    for unit in army_composition:
        name = unit["name"]
        count = unit["count"]
        slot = unit["slot"]
        category = unit.get("category", "troop") 
        
        if count <= 0:
            continue
            
        print(f"\n--- [Commander] Deploying {count}x {name} (Slot: {slot} | {category.upper()}) ---")
        
        if select_troop.select_troop(name, slot):
            bunches = troop_calculator.calculate_bunches(count) if category == "troop" else [1] * count
            deploy_swarm.deploy_swarm(name, category, bunches, all_side_points, panic_points, chosen_side_name)
        else:
            print(f" [Commander] Skipping {name} due to selection error.")
            
    print("\n=== [Commander] ALL TROOPS DEPLOYED. WAITING FOR BATTLE END ===")
    return True