import time
from config import find_and_click, read_damage, read_loot, save_debug_screenshot

# --- NEW: Import the deployment muscle from your new file! ---
from tactics import execute_randomized_drops

def deploy_troops(starting_gold, starting_elixir):
    
    # 1. Call the tactics file to physically drop the army
    deployment_success = execute_randomized_drops()
    
    # If it couldn't find the troops, skip the monitoring completely
    if not deployment_success:
        return 
        
    # 2. Wait for UI and set up the camera
    print(" [Attack] Deployment phase complete. Waiting for UI to update...")
    time.sleep(3) 
    
    save_debug_screenshot()
    print(" [Attack] Mid-battle calibration screenshot saved!")
    
    # 3. Launch the Live Telemetry Monitor
    print(" [Attack] Initiating Live Telemetry Monitor...")
    
    loot_met_streak = 0
    damage_met_streak = 0
    
    while True:
        if find_and_click("return_home.png", click=False) or find_and_click("okay.png", click=False):
            print(" [Monitor] Battle ended naturally.")
            break
            
        current_damage = read_damage()
        current_gold, current_elixir = read_loot()
        
        print(f"   --> Live Stats: {current_damage}% Damage | Gold: {current_gold:,} | Elixir: {current_elixir:,}")
        
        if 85 <= current_damage <= 100:
            damage_met_streak += 1
            if damage_met_streak >= 2: 
                print(" [Monitor] SUCCESS: 85%+ Damage confirmed! Pulling the plug.")
                break
            else:
                print(f"       [?] High damage detected. Verifying ({damage_met_streak}/2)...")
        else:
            damage_met_streak = 0 
            
        if current_gold <= (starting_gold * 0.15) and starting_gold > 0:
            loot_met_streak += 1
            if loot_met_streak >= 3:
                print(" [Monitor] SUCCESS: Loot secured confirmed! Pulling the plug.")
                break
            else:
                print(f"       [?] Low loot detected. Verifying ({loot_met_streak}/3)...")
        else:
            loot_met_streak = 0 
            
        time.sleep(1)