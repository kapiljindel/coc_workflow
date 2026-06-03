import sys
import start
import loot_checker
import attack
import attack_end
import cg_storage_checker   # --- NEW: Import the new storage checker with Telegram alerts!
# import upgrade       # --- NEW: Imported the Builder!

print("--- CoC Modular Bot Active ---")

try:
    while True:
        start.go_to_base()
        
        attack_finished = False
        while not attack_finished:
            should_attack, target_gold, target_elixir = loot_checker.evaluate_base()
            
            if should_attack:
                attack.deploy_troops(target_gold, target_elixir)
                attack_finished = True 
                
        attack_end.return_home()
        
        # --- NEW: Call the Builder before starting the next run! ---
        # upgrade.dump_excess_loot()
          
        cg_storage_checker.check_home_loot()


        print("\n--- Cycle Complete. Starting next run! ---")

except KeyboardInterrupt:
    print("\n [!] Bot stopped by user. Exiting gracefully.")
    sys.exit()