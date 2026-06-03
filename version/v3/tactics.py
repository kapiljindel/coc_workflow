import time
import random
from config import find_and_click, read_troops, device

def execute_randomized_drops():
    """Handles the physical, humanized dropping of troops."""
    print(" [Tactics] Deploying Swarm! Executing Undetectable Humanized Tactics...")
    
    if find_and_click("barbarian.png"):
        print(" [Tactics] Barbarian selected. Checking troop reserves...")
        time.sleep(0.5) 
        
        safe_zones = [
            (20, 100, 150, 550),    # Left outer grass
            (1150, 1250, 150, 550), # Right outer grass
            (200, 1000, 600, 680),  # Bottom outer grass
            (200, 1000, 50, 150)    # Top outer grass
        ]
        
        total_clusters = random.randint(4, 7)
        
        for i in range(total_clusters):
            current_troops = read_troops()
            
            # Anti-Glitch Double Check
            if current_troops <= 0:
                print(" [Tactics] Troop reader saw 0. Double-checking...")
                time.sleep(0.2) 
                current_troops = read_troops()
                
                if current_troops <= 0:
                    print(" [Tactics] Confirmed out of troops! Halting deployment early.")
                    break
                else:
                    print(f" [Tactics] Glitch avoided! Found {current_troops} troops.")
                
            hold_time = random.randint(500, 2500)
            print(f" [Tactics] Drop {i+1}/{total_clusters} ({current_troops} reserves) -> Holding for {hold_time}ms...")
            
            zone = random.choice(safe_zones)
            drop_x = random.randint(zone[0], zone[1])
            drop_y = random.randint(zone[2], zone[3])
            
            device.shell(f"input swipe {drop_x} {drop_y} {drop_x} {drop_y} {hold_time}")
            
            human_pause = random.uniform(0.1, 0.5)
            time.sleep(human_pause) 
            
        # Return True because the deployment was successfully executed
        return True
        
    else:
        print(" [Tactics] WARNING: Could not find troop icon to deploy!")
        # Return False so the monitor knows the attack failed to start
        return False