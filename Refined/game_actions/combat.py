"""
Combat Module
Orchestrates the attack phase after reaching a base
"""

import time
import random
from typing import Tuple

from utils.vision import find_and_click, read_loot, save_debug_screenshot
from utils.logger import get_logger
from config.constants import (
    LOOT_STABILIZATION_CHECK_MIN,
    LOOT_STABILIZATION_CHECK_MAX,
    ATTACK_DURATION_MIN,
    ATTACK_DURATION_MAX,
)
from tactics.strategy import execute_full_army_attack

logger = get_logger(__name__)

def deploy_troops(starting_gold: int, starting_elixir: int) -> bool:
    """
    Execute a complete attack from start to finish
    
    Args:
        starting_gold: Gold at battle start
        starting_elixir: Elixir at battle start
        
    Returns:
        True if attack completed
    """
    try:
        attack_start_time = time.time()
        max_attack_duration = random.randint(ATTACK_DURATION_MIN, ATTACK_DURATION_MAX)
        
        logger.info(f"⚔️  ATTACK INITIATED: Time limit set to {max_attack_duration}s")
        logger.info(f"Starting resources - Gold: {starting_gold:,} | Elixir: {starting_elixir:,}")
        
        # Wait for base to stabilize (loot values stop changing)
        logger.info("Waiting for base to stabilize...")
        stable_checks = 0
        last_g, last_e = -1, -1
        
        for _ in range(16):
            cg, ce = read_loot()
            if cg == last_g and ce == last_e:
                stable_checks += 1
                if stable_checks >= 2:
                    break
            else:
                stable_checks = 0
            
            last_g, last_e = cg, ce
            time.sleep(random.uniform(LOOT_STABILIZATION_CHECK_MIN, LOOT_STABILIZATION_CHECK_MAX))
        
        logger.info("✓ Base stabilized! Executing deployment...")
        save_debug_screenshot()
        
        # Execute troop deployment strategy
        from config.settings import get_config
        config = get_config()
        army_composition = config.get("MY_ARMY", [])
        
        deployment_success = execute_full_army_attack(army_composition)
        
        if not deployment_success:
            logger.error("Deployment failed. Bailing out.")
            return False
        
        logger.info("✓ Deployment phase complete. Waiting for UI...")
        time.sleep(random.uniform(2.5, 4.5))
        save_debug_screenshot()
        
        # Monitor battle until completion or time limit
        logger.info("Monitoring battle...")
        while True:
            elapsed_time = time.time() - attack_start_time
            
            # Check time limit
            if elapsed_time >= max_attack_duration:
                logger.info(f"⏱️  Time limit reached ({int(elapsed_time)}s). Ending battle.")
                break
            
            # Check if battle ended naturally
            if find_and_click("return_home.png", click=False) or find_and_click("okay.png", click=False):
                logger.info("✓ Battle ended naturally.")
                break
            
            # Light sleep to avoid CPU spike
            time.sleep(random.uniform(1.0, 2.0))
        
        logger.info("⚔️  ATTACK COMPLETE")
        return True
        
    except Exception as e:
        logger.error(f"Combat phase failed: {e}")
        return False
