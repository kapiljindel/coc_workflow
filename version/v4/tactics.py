import select_troop
import troop_calculator
import deploy_swarm
import base_scanner
from config import device, add_log

def execute_full_army_attack(army_composition):
    """
    Takes a full list of troops/heroes/spells, scans the base ONCE, 
    and executes deployments sequentially.
    """
    print("\n=== [Commander] INITIATING FULL ARMY ASSAULT ===")
    
    # Step 1: Scan the base ONCE for the entire attack
    print(" [Commander] Scanning base geometry...")
    screen_bytes = device.screencap()
    all_side_points, panic_points = base_scanner.get_safe_spam_points(screen_bytes)
    
    if not all_side_points:
        print(" [Commander] FATAL ERROR: Base scan failed. Aborting attack.")
        return False

    # Step 2: Loop through every unit in your army list
    for unit in army_composition:
        name = unit["name"]
        count = unit["count"]
        slot = unit["slot"]
        
        if count <= 0:
            continue
            
        print(f"\n--- [Commander] Deploying {count}x {name} (Slot: {slot}) ---")
        
        # Select the unit
        if select_troop.select_troop(name, slot):
            
            # Calculate bunches (if it's a hero with count=1, it will just return [1])
            bunches = troop_calculator.calculate_bunches(count)
            
            # Deploy using the base coordinates we scanned earlier!
            deploy_swarm.deploy_swarm(name, bunches, all_side_points, panic_points)
            
        else:
            print(f" [Commander] Skipping {name} due to selection error.")
            
    print("\n=== [Commander] ALL TROOPS DEPLOYED. WAITING FOR BATTLE END ===")
    return True