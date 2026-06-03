import time
import random
from config import find_and_click, device

# --- CONFIGURATION ---
# Set this to your actual total troop capacity!
TOTAL_TROOPS = 120  

def allocate_troops(total, num_bunches):
    """Mathematically breaks the total army into random, unpredictable chunks."""
    if total < num_bunches: 
        return [1] * total 
        
    points = sorted(random.sample(range(1, total), num_bunches - 1))
    bunches = [j - i for i, j in zip([0] + points, points + [total])]
    
    random.shuffle(bunches) 
    return bunches

def execute_randomized_drops():
    """
    Handles the high-speed, humanized deployment.
    Includes Red-Zone error handling and Persistent Image Verification.
    """
    print(f" [Tactics] Initiating Smart-Chunk Deployment for {TOTAL_TROOPS} troops...")
    
    # 1. Look for the active colored troop card
    if find_and_click("dragon.png"):
        print(" [Tactics] 'dragon.png' selected. Calculating deployment...")
        time.sleep(random.uniform(0.1, 0.25)) 
        
        # 8 Edge Vectors for deployment (based on your marked image)
        attack_paths = [
            (600, 100, 200, 300),   (600, 100, 1000, 300),  
            (1150, 375, 800, 150),  (1150, 375, 800, 600),  
            (600, 650, 200, 450),   (600, 650, 1000, 450),  
            (100, 375, 400, 150),   (100, 375, 400, 600)    
        ]
        
        # 2. Divide army into 4 to 8 bunches
        num_bunches = random.randint(4, 8)
        bunches = allocate_troops(TOTAL_TROOPS, num_bunches)
        print(f" [Tactics] Divided into {num_bunches} bunches: {bunches}")

        # 3. Main Deployment Loop (with Error Handling)
        i = 0
        while i < len(bunches):
            troops_to_drop = bunches[i]
            if troops_to_drop <= 0:
                i += 1
                continue
            
            # Select a random point on a random edge
            path = random.choice(attack_paths)
            progress = random.uniform(0.1, 0.9)
            base_x = int(path[0] + (path[2] - path[0]) * progress)
            base_y = int(path[1] + (path[3] - path[1]) * progress)
            
            drop_x = base_x + random.randint(-20, 20)
            drop_y = base_y + random.randint(-20, 20)
            
            # Calculate hold time (ms) based on troop count
            hold_time = random.randint(120, 180) + (troops_to_drop * random.randint(70, 95))
            
            # Execute the tap/hold with human-like jitter
            end_x = drop_x + random.randint(-3, 3)
            end_y = drop_y + random.randint(-3, 3)
            
            print(f" [Tactics] Chunk {i+1}/{len(bunches)}: {troops_to_drop} troops -> {hold_time}ms")
            device.shell(f"input swipe {drop_x} {drop_y} {end_x} {end_y} {hold_time}")
            
            # Human reaction time to check for errors
            time.sleep(random.uniform(0.15, 0.25)) 
            
            # ERROR CHECK: If we hit a red zone, don't move to next chunk
            if find_and_click("red_area_error.png", click=False, threshold=0.7):
                print("   [!] RED ZONE DETECTED! Repositioning this chunk...")
                time.sleep(random.uniform(0.2, 0.4))
                continue # Retry this same index 'i'
            else:
                i += 1 # Success, move to next bunch
                # Lightning-fast gap between bunches (ms)
                time.sleep(random.uniform(0.02, 0.08)) 

        # 4. PERSISTENT VERIFICATION LOOP
        print(" [Tactics] Deployment phase done. Starting persistent verification...")
        time.sleep(0.8)
        
        max_retries = 5
        for retry in range(max_retries):
            # Check for the Grey/End image
            if find_and_click("end_dragon.png", click=False, threshold=0.85):
                print(f" [Tactics] SUCCESS: All troops deployed (Verified on try {retry+1})")
                return True
            
            # If colored card still exists, panic dump
            print(f" [Tactics] WARNING: Troops remaining (Try {retry+1}/{max_retries})")
            
            path = random.choice(attack_paths)
            progress = random.uniform(0.2, 0.8)
            p_x = int(path[0] + (path[2] - path[0]) * progress)
            p_y = int(path[1] + (path[3] - path[1]) * progress)
            
            # Emergency 4-second hold
            panic_hold = random.randint(3500, 4500)
            device.shell(f"input swipe {p_x} {p_y} {p_x+2} {p_y-2} {panic_hold}")
            
            time.sleep(1.0) # Wait for UI to update

        return True
        
    else:
        print(" [Tactics] ERROR: 'dragon.png' not found on screen.")
        return False