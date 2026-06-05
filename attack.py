import time
import random
from config import find_and_click, read_damage, read_loot, save_debug_screenshot, MY_ARMY, get_current_screen
import tactics

def deploy_troops(starting_gold, starting_elixir):
    
    attack_start_time = time.time()
    max_attack_duration = random.randint(30, 40)
    print(f"\n [Attack] FUSE LIT: Total time limit set to {max_attack_duration} seconds!")
    
    print(" [Attack] Waiting for clouds to clear and base to load...")
    stable_checks = 0
    last_g, last_e = -1, -1
    
    for _ in range(16): 
        # Using the default screen grab here is fine since it's a slow loop
        cg, ce = read_loot()
        if cg == last_g and ce == last_e:
            stable_checks += 1
            if stable_checks >= 2: 
                break
        else:
            stable_checks = 0
            
        last_g, last_e = cg, ce
        time.sleep(random.uniform(0.4, 0.7))
        
    print(" [Attack] Base stabilized! Executing deployment.")

    deployment_success = tactics.execute_full_army_attack(MY_ARMY)
    
    if not deployment_success:
        print(" [Attack] Deployment failed. Bailing out.")
        return 
        
    print(" [Attack] Deployment phase complete. Waiting for UI...")
    time.sleep(random.uniform(2.5, 4.5)) 
    
    save_debug_screenshot()
    
    # --- OPTIMIZED: Live Telemetry Monitor & Stats completely removed for speed ---
    
    while True:
        elapsed_time = time.time() - attack_start_time
        
        # 1. Check if the maximum time limit has been reached
        if elapsed_time >= max_attack_duration:
            print(f" [Monitor] TRUE TIME LIMIT REACHED ({int(elapsed_time)}s). Bailing out for faster farming!")
            break

        # 2. Check if the battle ended naturally (detecting the end buttons)
        if find_and_click("return_home.png", click=False) or find_and_click("okay.png", click=False):
            print(" [Monitor] Battle ended naturally.")
            break
            
        # Light sleep to prevent the CPU from redlining while waiting for the match to finish
        time.sleep(random.uniform(1.0, 2.0))