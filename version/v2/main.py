import sys
import start
import loot_checker   # --- NEW!
import attack
import attack_end

print("--- CoC Modular Bot Active ---")

try:
    while True:
        # Step 1: Get into matchmaking clouds
        start.go_to_base()
        
        # Step 2: The Scouting Loop
        attack_finished = False
        while not attack_finished:
            
            # Ask the scout if the base is good
            should_attack = loot_checker.evaluate_base()
            
            # Step 3: If the scout says yes, send in the General!
            if should_attack:
                attack.deploy_troops()
                attack_finished = True # This breaks the scouting loop!
                
        # Step 4: Attack is over, clean up the screen and return home
        attack_end.return_home()
        
        print("\n--- Cycle Complete. Starting next run! ---")

except KeyboardInterrupt:
    print("\n [!] Bot stopped by user. Exiting gracefully.")
    sys.exit()