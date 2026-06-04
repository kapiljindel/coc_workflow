"""
Cleanup Module
Handles returning home and cleanup after battle
"""

import time
import random
import os

from utils.vision import find_and_click
from utils.logger import get_logger
from config.constants import (
    RETRY_DELAY_MIN,
    RETRY_DELAY_MAX,
    SURRENDER_CONFIRM_MIN,
    SURRENDER_CONFIRM_MAX,
    BATTLE_SUMMARY_TRANSITION_MIN,
    BATTLE_SUMMARY_TRANSITION_MAX,
    RETURN_HOME_MIN,
    RETURN_HOME_MAX,
)

logger = get_logger(__name__)

def return_home() -> bool:
    """
    Return to home village after battle
    
    Steps:
    1. Click Surrender or End Battle
    2. Confirm with Okay
    3. Click Return Home
    4. Wait for home to load
    5. Delete debug images
    
    Returns:
        True on success
    """
    try:
        logger.info("Cleaning up battle...")
        
        # Click surrender/end battle
        for attempt in range(3):
            if find_and_click("surrender.png") or find_and_click("end_battle.png"):
                logger.info("Battle ended")
                time.sleep(random.uniform(SURRENDER_CONFIRM_MIN, SURRENDER_CONFIRM_MAX))
                
                # Confirm popup
                find_and_click("okay.png")
                
                # Wait for battle summary screen
                time.sleep(random.uniform(BATTLE_SUMMARY_TRANSITION_MIN, BATTLE_SUMMARY_TRANSITION_MAX))
                break
            
            time.sleep(random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX))
        
        # Return to home
        logger.info("Returning to home village...")
        attempts = 0
        while not (find_and_click("return_home.png") or find_and_click("okay.png")):
            time.sleep(random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX))
            attempts += 1
            if attempts > 20:
                logger.warning("Timeout returning home")
                break
        
        logger.info("✓ Returned to home village")
        
        # Clean up debug images
        debug_files = [
            "img/calibration_screen.png",
            "img/debug_gold.png",
            "img/debug_elixir.png",
            "img/debug_home_gold.png",
            "img/debug_home_elixir.png",
        ]
        
        for filepath in debug_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
        
        logger.info("✓ Cleaned up debug images")
        
        # Wait for home village to fully render
        time.sleep(random.uniform(RETURN_HOME_MIN, RETURN_HOME_MAX))
        
        return True
        
    except Exception as e:
        logger.error(f"Return home failed: {e}")
        return False
