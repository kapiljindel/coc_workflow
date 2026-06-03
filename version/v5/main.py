import sys, time, random
import start, loot_checker, attack, attack_end, cg_storage_checker
from config import flush_logs, add_log, find_and_click, device

print("--- CoC Pro-Bot Active ---")

try:
    while True:
        start.go_to_base()
        
        attack_finished = False
        next_counter = 0 
        
        while not attack_finished:
            # --- PATTERN BREAKER (REST ONLY) ---
            break_threshold = random.randint(10, 15)
            if next_counter >= break_threshold:
                print(f"\n [Search] Anti-Detection: Resting for 60s after {next_counter} skips.")
                add_log("attack", f"Anti-Detection: Resting for 60s after {next_counter} skips.")
                attack_end.return_home()
                time.sleep(60) 
                attack_finished = True
                break 

            # --- STRICT SEARCHING ---
            should_attack, g, e = loot_checker.evaluate_base()

            if should_attack:
                # LOOT IS GOOD: Attack!
                print(f"\n [Search] JACKPOT! Starting Attack. Gold: {g} | Elixir: {e}")
                add_log("resources", f"Attack Started. Gold: {g} | Elixir: {e}")
                
                attack.deploy_troops(g, e) 
                attack_finished = True 
                
            else:
                # LOOT IS BAD: Click Next!
                next_counter += 1
                print(f" [Search] Loot too low. Clicking NEXT... (Skips: {next_counter})")
                
                if not find_and_click("next.png", threshold=0.7):
                    # Failsafe tap directly on the orange Next button
                    device.shell("input tap 1450 750") 
                    
                # Wait for the clouds to clear before checking the next base
                time.sleep(random.uniform(3.0, 5.0))

        # After the attack (or rest) finishes, go home and check storages
        attack_end.return_home()
        cg_storage_checker.check_home_loot()
        
        flush_logs()
        print("--- Cycle Complete. Logs Saved. ---")

except KeyboardInterrupt:
    flush_logs()
    print("\n [System] Bot stopped safely.")
    sys.exit()