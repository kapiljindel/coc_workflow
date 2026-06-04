"""
Scouting Module
Evaluates bases and determines if they're worth attacking
"""

import time
import random
import os
from typing import Tuple

from utils.vision import find_and_click, read_loot, save_debug_screenshot
from utils.logger import get_logger
from config.constants import (
    HUMAN_REACTION_TIME_MIN,
    HUMAN_REACTION_TIME_MAX,
    CLOUD_LOAD_TIME_EXTENDED_MIN,
    CLOUD_LOAD_TIME_EXTENDED_MAX,
    MINIMUM_GOLD,
    MINIMUM_ELIXIR,
)

logger = get_logger(__name__)

def evaluate_base() -> Tuple[bool, int, int]:
    """
    Evaluate if a loaded base is worth attacking
    
    Steps:
    1. Wait for human reaction time
    2. Read loot values
    3. Compare against thresholds
    4. Click Next if trash base or return result if good
    
    Returns:
        (should_attack, gold, elixir) tuple
    """
    try:
        # Human reaction time before making a decision
        time.sleep(random.uniform(HUMAN_REACTION_TIME_MIN, HUMAN_REACTION_TIME_MAX))
        
        logger.info("Scanning base loot...")
        save_debug_screenshot()
        
        current_gold, current_elixir = read_loot()
        logger.info(f"Detected Gold: {current_gold:,} | Elixir: {current_elixir:,}")
        
        # Check if base is worth attacking
        if current_gold >= MINIMUM_GOLD or current_elixir >= MINIMUM_ELIXIR:
            logger.info(f"JACKPOT! Gold: {current_gold:,} >= {MINIMUM_GOLD:,} OR Elixir: {current_elixir:,} >= {MINIMUM_ELIXIR:,}")
            return True, current_gold, current_elixir
        
        # Trash base - click Next
        logger.info("Trash base. Clicking Next...")
        
        # Cleanup debug files
        debug_files = ["calibration_screen.png", "debug_gold.png", "debug_elixir.png"]
        for filename in debug_files:
            path = os.path.join("img", filename)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        # Click Next button
        if find_and_click("next_base.png"):
            # Wait for clouds to clear
            time.sleep(random.uniform(CLOUD_LOAD_TIME_EXTENDED_MIN, CLOUD_LOAD_TIME_EXTENDED_MAX))
            return False, 0, 0
        else:
            logger.warning("'Next' button missing! Timer likely expired.")
            return True, current_gold, current_elixir
        
    except Exception as e:
        logger.error(f"Base evaluation failed: {e}")
        return False, 0, 0
