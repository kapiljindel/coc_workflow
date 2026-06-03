import time
import random
from config import find_and_click, read_damage, read_loot, save_debug_screenshot
import tactics

def deploy_troops(starting_gold, starting_elixir):
    
    # --- NEW: THE COMMANDER LOADOUT ---
    # Update this list with exactly what troops you have, what their image name is, 
    # and which slot box they are sitting in! (I set this up based on your screenshots)
    # If you don't have a troop or hero for an attack, just set the count to 0!
    my_army = [
        {"name": "dragon",   "count": 9, "slot": "troop_1"},
        {"name": "minion",   "count": 0, "slot": "troop_2"}, # Example of an empty slot
        {"name": "king",     "count": 1, "slot": "hero_1"},
        {"name": "queen",    "count": 1, "slot": "hero_2"},
        {"name": "warden",   "count": 1, "slot": "hero_3"},
        {"name": "rage",     "count": 4, "slot": "spell_1"},
        {"name": "freeze",   "count": 1, "slot": "spell_2"},
    ]
    
    # 1. Hand the loadout to the Commander to scan the base and drop everything!
    deployment_success = tactics.execute_full_army_attack(my_army)
    
    # If it couldn't find the base or completely failed, skip the monitoring
    if not deployment_success:
        print(" [Attack] Deployment failed or aborted. Skipping telemetry.")
        return 
        
    # 2. Wait for UI and set up the camera
    print(" [Attack] Deployment phase complete. Waiting for UI to update...")
    time.sleep(random.uniform(2.5, 4.5)) 
    
    save_debug_screenshot()
    print(" [Attack] Mid-battle calibration screenshot saved!")
    
    # 3. Launch the Live Telemetry Monitor
    print(" [Attack] Initiating Live Telemetry Monitor...")
    
    loot_met_streak = 0
    damage_met_streak = 0
    
    target_exit_damage = random.randint(75, 85)
    print(f" [Attack] Target damage to reach before exiting: {target_exit_damage}%")
    
    while True:
        # Check if the battle ended on its own (troops died, time ran out)
        if find_and_click("return_home.png", click=False) or find_and_click("okay.png", click=False):
            print(" [Monitor] Battle ended naturally.")
            break
            
        current_damage = read_damage()
        current_gold, current_elixir = read_loot()
        
        print(f"   --> Live Stats: {current_damage}% Damage | Gold: {current_gold:,} | Elixir: {current_elixir:,}")
        
        if current_damage >= target_exit_damage:
            damage_met_streak += 1
            if damage_met_streak >= 2: 
                print(f" [Monitor] SUCCESS: {target_exit_damage}%+ Damage confirmed! Pulling the plug.")
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
            
        time.sleep(random.uniform(1.2, 2.6))