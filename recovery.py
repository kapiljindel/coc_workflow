import time
import os
import sys
from config import find_and_click, device, add_log

def rescue_bot():
    print("\n [WATCHDOG] 🚨 5-Minute Timeout Triggered! Executing Emergency Recovery...")
    add_log("errors", "Watchdog triggered. Attempting recovery.")

    # 1. Restart the Game via ADB
    print(" [RECOVERY] Force restarting Clash of Clans...")
    try:
        device.shell("am force-stop com.supercell.clashofclans")
        time.sleep(3)
        device.shell("monkey -p com.supercell.clashofclans -c android.intent.category.LAUNCHER 1")
        print(" [RECOVERY] App launched. Giving it 20 seconds to boot up...")
        time.sleep(20) 
    except Exception as e:
        print(f" [RECOVERY] ADB Restart Failed: {e}")

    # 2. Clear Startup Pop-ups ("You were raided", "Offers", etc.)
    print(" [RECOVERY] Clearing welcome pop-ups...")
    # for _ in range(3):
    #     # Tap the top-left corner (empty grass) to bypass generic click-to-close screens
    #     device.shell("input tap 100 100") 
    #     time.sleep(1)
        
        # Look for the specific "Okay" button if it's a standard pop-up
        # find_and_click("okay.png")
        # time.sleep(1.5)

    # 3. THE MAGIC TRICK: Completely reboot the Python script
    print(" [RECOVERY] Rebooting the Python Bot to perfectly sync with the game...")
    time.sleep(2)
    
    # This line kills the current script and starts main.py over from the very beginning!
    os.execl(sys.executable, sys.executable, *sys.argv)