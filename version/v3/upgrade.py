import time
from config import find_and_click, device

def dump_excess_loot():
    print("\n [Builder] Scanning base for upgradable walls...")
    
    wall_found = False
    
    # --- NEW: The Image Scanner List ---
    # You can add as many wall images to this list as you want!
    wall_images = [ "wall2.png", ]
    
    for wall_img in wall_images:
        # We search for the image, and if found, find_and_click automatically taps it!
        if find_and_click(wall_img, threshold=0.8):
            print(f" [Builder] Target acquired! Tapped wall using {wall_img}.")
            wall_found = True
            time.sleep(1) # Wait for the bottom UI menu to pop up
            break # Stop searching the list because we already clicked one
            
    if not wall_found:
        print(" [Builder] Could not find any matching walls on the screen.")
        return False
        
    # 2. Click the hammer button you cropped!
    if find_and_click("upgrade_menu.png", threshold=0.8):
        print(" [Builder] Upgrade menu opened. Looking for confirm button...")
        time.sleep(1) 
        
        # 3. Look for the Green Confirm Buttons!
        if find_and_click("confirm_elixir.png", threshold=0.8):
            print(" [Builder] SUCCESS: Dumped excess Elixir into the wall!")
        elif find_and_click("confirm_gold.png", threshold=0.8):
            print(" [Builder] SUCCESS: Dumped excess Gold into the wall!")
        else:
            print(" [Builder] Not enough loot to upgrade.")
            
        # Tap a safe spot (top-left) to close the confirm menu if we couldn't afford it
        device.shell("input tap 50 50")
        time.sleep(0.5)
        
    else:
        print(" [Builder] Wall is maxed for this Town Hall or menu didn't open.")
        
    # Tap a safe spot again to deselect the wall
    device.shell("input tap 50 50")
    time.sleep(1)
    return True

# --- Testing Trigger ---
if __name__ == "__main__":
    dump_excess_loot()