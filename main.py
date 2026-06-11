import sys, time, random, threading, os
import start, loot_checker, attack, attack_end, cg_storage_checker, recovery
from config import flush_logs, add_log, find_and_click, device , IS_PUSH_JSON

# 🔥 IMPORT YOUR SEPARATE PIPELINE FILE HERE 🔥
import push_data

print("--- CoC Pro-Bot Active ---")
# BUILDER_LIST_REGION = (124, 685, 600, 1038)

# --- GLOBAL WATCHDOG TIMER ---
last_action_time = time.time()

def watchdog_monitor():
    global last_action_time
    while True:
        time.sleep(10) # Check the stopwatch every 10 seconds
        
        # If 300 seconds (5 minutes) have passed since the last action...
        if time.time() - last_action_time > 300:
            recovery.rescue_bot()
            
            # Reset the stopwatch so it doesn't immediately trigger again
            last_action_time = time.time() 

# Start the Watchdog in the background (daemon=True means it stops when the main script stops)
threading.Thread(target=watchdog_monitor, daemon=True).start()
# ----------------------------------

def rest_countdown(seconds):
    print() 
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02d}:{secs:02d}"
        print(f" [Rest] Cooling down to avoid detection... Resuming in {timer}   ", end="\r")
        time.sleep(1)
        seconds -= 1
    print("\n [Rest] Break complete. Booting up systems again!                    ")

# try:
#             push_data.execute_data_deployment_pipeline()
# except Exception as pipeline_err:
#             print(f"⚠️ [Pipeline Exception] Sync failed but continuing bot loop: {pipeline_err}")

# --- STATS COUNTERS ---
cycle_count = 0
attack_count = 0


try:
    while True:
        last_action_time = time.time() 
        
        
        # ==========================================================
        # 🔥 RUN SEPARATE DATA PIPELINE AT THE FIRST PLACE 🔥
        # ==========================================================
        if IS_PUSH_JSON:
            try:
                print(" [Pipeline] Executing data deployment pipeline...")
                # Calling the function from push_data.py
                push_data.execute_data_deployment_pipeline()
                print(" [Pipeline] Data sync successful.")
            except AttributeError as attr_err:
                print(f"❌ [Pipeline Error] The function name in push_data.py doesn't match: {attr_err}")
            except Exception as pipeline_err:
                print(f"⚠️ [Pipeline Exception] Sync failed but continuing bot loop: {pipeline_err}")
        else:
            print(" [Pipeline] Skipped (IS_PUSH_JSON is set to False in config)")
        
        # --- Check if the start sequence actually worked ---
        if not start.go_to_base():
            print(" [System] Start sequence got stuck. Triggering Recovery...")

        
        # --- Check if the start sequence actually worked ---
        if not start.go_to_base():
            print(" [System] Start sequence got stuck. Triggering Recovery...")
            recovery.rescue_bot() # Restart the game
            continue # This instantly jumps back to the top of the 'while True' loop!
        
        # ==========================================================
        # 🔥 RUN SEPARATE DATA PIPELINE AT THE FIRST PLACE 🔥
        # ==========================================================
        
        attack_completed = False
        rest_triggered = False
        next_counter = 0 
        
        while not attack_completed and not rest_triggered:
            break_threshold = random.randint(10, 15)
            if next_counter >= break_threshold:
                print(f"\n [Search] Anti-Detection: Triggered after {next_counter} skips.")
                add_log("attack", f"Anti-Detection: Resting after {next_counter} skips.")
                
                attack_end.return_home()
                rest_time = random.randint(55, 85)
                
                last_action_time = time.time() + rest_time 
                
                rest_countdown(rest_time)
                rest_triggered = True
                break 

            should_attack, g, e = loot_checker.evaluate_base()

            if should_attack:
                print(f"\n [Search] JACKPOT! Starting Attack. Gold: {g} | Elixir: {e}")
                add_log("resources", f"Attack Started. Gold: {g} | Elixir: {e}")
                
                attack.deploy_troops(g, e) 
                attack_completed = True 
                attack_count += 1  # Increment successful attack count
            else:
                next_counter += 1
                print(f" [Search] Loot too low. Clicking NEXT... (Skips: {next_counter})")
                
                if not find_and_click("next.png", threshold=0.7):
                    device.shell("input tap 1450 750") 
                    
                time.sleep(random.uniform(3.0, 5.0))

        if attack_completed:
            attack_end.return_home()
            
        cg_storage_checker.check_home_loot()
        flush_logs()
        print("--- Cycle Complete. Logs Saved. ---")
        
        # Increment the total loop runtime count
        cycle_count += 1
        
        # Give you 3 seconds to read the last cycle logs before clearing the screen
        time.sleep(3)
        
        # Clear terminal screen (cls for Windows, clear for Mac/Linux)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print Dashboard Tracker at the top of the freshly cleared screen
        print("=========================================")
        print("          --- CoC Pro-Bot ---            ")
        print(f"  Total Loop Cycles Run: {cycle_count}")
        print(f"  Total Attacks Executed: {attack_count}")
        print("=========================================\n")

except KeyboardInterrupt:
    flush_logs()
    print("\n [System] Bot stopped safely.")
    sys.exit()
except Exception as e:
    flush_logs()
    print(f"\n [CRITICAL ERROR] Bot crashed: {e}")
    sys.exit()