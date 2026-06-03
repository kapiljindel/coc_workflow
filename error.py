import time
import random
from config import find_and_click, add_log, device

def check_and_clear_popups():
    """
    Scans the screen for known interruptions (Star Bonus, Disconnects).
    Returns True if it fixed something, False if the screen is clear.
    """
    handled_something = False
    
    # 1. NETWORK ERROR / RELOAD GAME
    if find_and_click("reload_game.png") or find_and_click("try_again.png") or find_and_click("reconnect.png"):
        print("\n [Error Handler] Network/Reload popup detected. Reconnecting...")
        add_log("errors", "Network disconnect popup handled.")
        time.sleep(random.uniform(8.0, 14.0)) # Wait a long time for the game to reboot
        handled_something = True
        
    # 2. STAR BONUS OR DAILY REWARD
    # Usually you just need to click the generic 'okay.png' or an 'x' button
    elif find_and_click("star_bonus_x.png") or find_and_click("claim_reward.png"):
        print("\n [Error Handler] Dismissed Star Bonus or Daily Reward.")
        add_log("errors", "Cleared Star Bonus popup.")
        time.sleep(random.uniform(1.2, 2.5))
        handled_something = True

    # 3. PERSONAL BREAK (Kicked off for playing too long)
    elif find_and_click("personal_break.png"):
        print("\n [Error Handler] CRITICAL: Personal Break limit hit! Taking a forced nap.")
        add_log("errors", "Hit Supercell Personal Break limit.")
        # Sleep for 15 to 25 minutes to let the personal break reset
        time.sleep(60 * random.randint(15, 25)) 
        handled_something = True

    # 4. GENERIC OKAY BUTTON (Catches maintenance warnings, random popups)
    elif find_and_click("okay.png"):
        print("\n [Error Handler] Clicked generic 'Okay' popup.")
        time.sleep(random.uniform(1.5, 3.0))
        handled_something = True

    return handled_something

def hard_restart_game():
    """
    If the bot gets completely stuck (black screen, frozen), 
    this kills the CoC app in Bluestacks and boots it back up.
    """
    print("\n [Error Handler] Executing HARD RESTART of Clash of Clans...")
    add_log("errors", "Executed Hard Restart via ADB.")
    
    # Force stop the app
    device.shell("am force-stop com.supercell.clashofclans")
    time.sleep(random.uniform(2.5, 4.0))
    
    # Launch the app again
    device.shell("monkey -p com.supercell.clashofclans -c android.intent.category.LAUNCHER 1")
    
    # Give it plenty of time to get past the Supercell loading screen
    time.sleep(random.uniform(18.0, 25.0))
    print(" [Error Handler] Game Rebooted. Resuming bot operations.")