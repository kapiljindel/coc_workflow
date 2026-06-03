import sys
import start
import attack
import attack_end

print("--- CoC Modular Bot Active ---")

try:
    while True:
        # Step 1: Get into matchmaking
        start.go_to_base()
        
        # Step 2: Keep scanning and hitting 'Next' UNTIL an attack finishes
        attack_finished = False
        while not attack_finished:
            attack_finished = attack.evaluate_and_attack()
            
        # Step 3: We finished an attack, so clean up and go home
        attack_end.return_home()
        
        print("\n--- Cycle Complete. Starting next run! ---")

except KeyboardInterrupt:
    print("\n [!] Bot stopped by user. Exiting gracefully.")
    sys.exit()
