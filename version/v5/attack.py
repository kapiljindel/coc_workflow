import time
import random
from config import find_and_click, read_damage, read_loot, save_debug_screenshot, MY_ARMY
import tactics

def deploy_troops(starting_gold, starting_elixir):
    
    # --- FIXED: START THE TIMER IMMEDIATELY ---
    attack_start_time = time.time()
    max_attack_duration = random.randint(90, 120)
    print(f"\n [Attack] FUSE LIT: Total time limit set to {max_attack_duration} seconds!")
    
    # --- CLOUD & LOOT STABILIZER ---
    print(" [Attack] Waiting for clouds to clear and base to load...")
    stable_checks = 0
    last_g, last_e = -1, -1
    
    for _ in range(16): 
        cg, ce = read_loot()
        if cg == last_g and ce == last_e:
            stable_checks += 1
            if stable_checks >= 2: 
                break
        else:
            stable_checks = 0
            
        last_g, last_e = cg, ce
        time.sleep(0.5)
        
    print(" [Attack] Base stabilized! Executing deployment.")

    # 1. Drop the army
    deployment_success = tactics.execute_full_army_attack(MY_ARMY)
    
    if not deployment_success:
        print(" [Attack] Deployment failed. Bailing out.")
        return 
        
    # 2. Wait for UI
    print(" [Attack] Deployment phase complete. Waiting for UI...")
    time.sleep(random.uniform(2.5, 4.5)) 
    
    save_debug_screenshot()
    
    # 3. Live Telemetry Monitor
    print(" [Attack] Initiating Live Telemetry Monitor...")
    
    loot_met_streak = 0
    damage_met_streak = 0
    target_exit_damage = random.randint(75, 85)
    
    while True:
        # --- FIXED: CHECK THE TRUE ELAPSED TIME ---
        elapsed_time = time.time() - attack_start_time
        if elapsed_time >= max_attack_duration:
            print(f" [Monitor] TRUE TIME LIMIT REACHED ({int(elapsed_time)}s). Bailing out for faster farming!")
            break

        if find_and_click("return_home.png", click=False) or find_and_click("okay.png", click=False):
            print(" [Monitor] Battle ended naturally.")
            break
            
        current_damage = read_damage()
        current_gold, current_elixir = read_loot()
        
        print(f"   --> Live Stats: {current_damage}% Damage | Gold: {current_gold:,} | Elixir: {current_elixir:,} | Time: {int(elapsed_time)}s")
        
        if current_damage >= target_exit_damage:
            damage_met_streak += 1
            if damage_met_streak >= 2: 
                print(f" [Monitor] SUCCESS: {target_exit_damage}%+ Damage confirmed! Pulling the plug.")
                break
        else:
            damage_met_streak = 0 
            
        if current_gold <= (starting_gold * 0.15) and starting_gold > 0:
            loot_met_streak += 1
            if loot_met_streak >= 3:
                print(" [Monitor] SUCCESS: Loot secured confirmed! Pulling the plug.")
                break
        else:
            loot_met_streak = 0 
            
        time.sleep(random.uniform(1.2, 2.6))