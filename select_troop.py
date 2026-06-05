import time
import random
from config import device, ARMY_SLOTS, add_log

def select_troop(troop_name, slot_name):
    print(f" [Select] Tapping {slot_name} for {troop_name}...")
    
    if slot_name not in ARMY_SLOTS:
        print(f" [Select] ERROR: Slot {slot_name} does not exist in config!")
        return False
        
    y1, y2, x1, x2 = ARMY_SLOTS[slot_name]
    
    # Calculate a random pixel inside the yellow box
    tap_x = random.randint(x1 + 10, x2 - 10)
    tap_y = random.randint(y1 + 10, y2 - 10)
    
    device.shell(f"input tap {tap_x} {tap_y}")
    
    time.sleep(random.uniform(0.05, 0.08)) 
    return True