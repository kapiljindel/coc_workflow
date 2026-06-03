import sys, time, random
import start, loot_checker, attack, attack_end, cg_storage_checker
from config import flush_logs, add_log

next_counter = 0
force_attack_mode = False
force_attack_count = 0

print("--- CoC Pro-Bot Active ---")

try:
    while True:
        start.go_to_base()
        
        attack_finished = False
        next_counter = 0 
        
        while not attack_finished:
            # --- PATTERN BREAKER ---
            # If we've skipped 10-15 bases, do something random to hide bot behavior
            break_threshold = random.randint(10, 15)
            
            if next_counter >= break_threshold and not force_attack_mode:
                decision = random.choice(["REST", "FORCE"])
                if decision == "REST":
                    add_log("attack", f"Anti-Detection: Resting for 60s after {next_counter} skips.")
                    attack_end.return_home()
                    time.sleep(60) 
                    attack_finished = True
                    break 
                else:
                    add_log("attack", "Anti-Detection: Entering Force-Attack mode (2-5 bases).")
                    force_attack_mode = True
                    force_attack_count = random.randint(2, 5)

            # --- SEARCHING ---
            should_attack, g, e = loot_checker.evaluate_base()
            
            # If Force Attack is on, we skip the loot check and just go in
            if force_attack_mode:
                should_attack = True
                force_attack_count -= 1
                if force_attack_count <= 0: force_attack_mode = False

            if should_attack:
                add_log("resources", f"Attack Started. Gold: {g} | Elixir: {e}")
                attack.deploy_troops(g, e)
                attack_finished = True 
            else:
                next_counter += 1
                # Small human-like delay between "Next" clicks
                time.sleep(random.uniform(0.5, 1.5))

        attack_end.return_home()
        cg_storage_checker.check_home_loot()
        
        # SAVE ALL LOGS TO THE FOLDER AFTER THE ATTACK IS TOTALLY DONE
        flush_logs()
        print("--- Cycle Complete. Logs Saved. ---")

except KeyboardInterrupt:
    flush_logs()
    sys.exit()