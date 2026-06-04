"""
Navigation Module
Handles navigating to bases and finding matches
"""

import time
import random
from utils.vision import find_and_click
from utils.logger import get_logger
from config.constants import (
    RETRY_DELAY_MIN,
    RETRY_DELAY_MAX,
    UI_TRANSITION_MIN,
    UI_TRANSITION_MAX,
    CLOUD_LOAD_TIME_MIN,
    CLOUD_LOAD_TIME_MAX,
)

logger = get_logger(__name__)

def go_to_base() -> bool:
    """
    Navigate to a base to attack
    
    Steps:
    1. Open Map
    2. Click Find Match
    3. Click Single Player Attack
    4. Wait for cloud to clear
    
    Returns:
        True on success, False on timeout
    """
    try:
        logger.info("Opening Map...")
        attempts = 0
        while not (find_and_click("main_attack.png") or 
                  find_and_click("main_attack_low.png") or 
                  find_and_click("main_attack_4.png")):
            time.sleep(random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX))
            attempts += 1
            if attempts > 15:
                logger.error("Timeout waiting for Map button!")
                return False
        
        time.sleep(random.uniform(UI_TRANSITION_MIN, UI_TRANSITION_MAX))
        
        logger.info("Clicking Find Match...")
        attempts = 0
        while not find_and_click("find_match.png"):
            time.sleep(random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX))
            attempts += 1
            if attempts > 15:
                logger.error("Timeout waiting for Find Match button!")
                return False
        
        time.sleep(random.uniform(UI_TRANSITION_MIN, UI_TRANSITION_MAX))
        
        logger.info("Clicking Attack Button...")
        attempts = 0
        while not find_and_click("single_player_attack.png"):
            time.sleep(random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX))
            attempts += 1
            if attempts > 15:
                logger.error("Timeout waiting for Attack button!")
                return False
        
        logger.info("Searching the clouds...")
        time.sleep(random.uniform(CLOUD_LOAD_TIME_MIN, CLOUD_LOAD_TIME_MAX))
        
        logger.info("✓ Base loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        return False
