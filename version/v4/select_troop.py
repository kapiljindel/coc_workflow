import time
import random
# --- Import the new ARMY_SLOTS dictionary ---
from config import find_and_click, add_log, device, ARMY_SLOTS

def select_troop(troop_name, slot_name):
    active_image = f"{troop_name}.png"
    print(f" [Select] Attempting to select {troop_name} in slot {slot_name}...")
    
    # 1. Try the smart way (Image Recognition)
    if find_and_click(active_image, threshold=0.70):
        print(f" [Select] '{active_image}' selected via visual match.")
        time.sleep(random.uniform(0.1, 0.25)) 
        return True
        
    # 2. Try the brute-force way (Using the specific slot coordinate)
    else:
        print(f" [Select] WARNING: Visual match failed! Tapping slot '{slot_name}'...")
        
        if slot_name not in ARMY_SLOTS:
            print(f" [Select] ERROR: Slot {slot_name} does not exist in config.py!")
            return False
            
        y1, y2, x1, x2 = ARMY_SLOTS[slot_name]
        
        tap_x = random.randint(x1 + 10, x2 - 10)
        tap_y = random.randint(y1 + 10, y2 - 10)
        
        time.sleep(random.uniform(0.2, 0.4))
        device.shell(f"input tap {tap_x} {tap_y}")
        print(f" [Select] Failsafe tap executed at ({tap_x}, {tap_y})")
        
        time.sleep(random.uniform(0.1, 0.25)) 
        return True