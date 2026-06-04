"""
Strategy Module
Orchestrates the overall battle tactics and troop deployment
"""

import random
from typing import List, Dict

from utils.logger import get_logger
from utils.adb_connector import get_device
from tactics.troop_selection import select_troop
from tactics.troop_planning import calculate_bunches
from tactics.deployment import deploy_swarm
from tactics.base_analysis import get_safe_spam_points

logger = get_logger(__name__)

def execute_full_army_attack(army_composition: List[Dict]) -> bool:
    """
    Execute complete army deployment strategy
    
    Steps:
    1. Scan base for tactical points
    2. Choose deployment side
    3. Deploy each unit in army composition
    4. Return success status
    
    Args:
        army_composition: List of unit dicts with name, count, category
        
    Returns:
        True if all troops deployed successfully
    """
    try:
        logger.info("=" * 60)
        logger.info("⚔️  INITIATING FULL ARMY ASSAULT")
        logger.info("=" * 60)
        
        # Scan base geometry
        logger.info("Scanning base geometry for tactical points...")
        device = get_device()
        if device is None:
            logger.error("Device not connected!")
            return False
        
        screen_bytes = device.screencap()
        all_side_points, panic_points = get_safe_spam_points(screen_bytes)
        
        if not all_side_points:
            logger.error("🔴 FATAL ERROR: Base scan failed!")
            return False
        
        # Choose deployment side
        chosen_side_name = random.choice(list(all_side_points.keys()))
        logger.info(f"✓ Master Tactical Vector Locked: {chosen_side_name}")
        logger.info(f"✓ Available deployment points: {sum(len(p) for p in all_side_points.values())}")
        
        # Deploy each unit in the army
        deployment_count = 0
        for unit in army_composition:
            name = unit.get("name", "unknown")
            count = unit.get("count", 0)
            slot = unit.get("slot", "unknown")
            category = unit.get("category", "troop")
            
            if count <= 0:
                logger.debug(f"Skipping {name} (count=0)")
                continue
            
            logger.info(f"\n▶ Deploying {count}x {name.upper()} [Slot: {slot} | {category}]")
            
            # Select the troop
            if not select_troop(name, slot):
                logger.warning(f"⚠️  Could not select {name}, skipping...")
                continue
            
            # Calculate bunches for troops
            if category == "troop":
                bunches = calculate_bunches(count)
                logger.debug(f"Bunches: {bunches}")
            else:
                # Heroes and spells deploy as singles
                bunches = [1] * count
            
            # Deploy the swarm
            if deploy_swarm(name, category, bunches, all_side_points, panic_points, chosen_side_name):
                deployment_count += 1
                logger.info(f"✓ {name.upper()} deployed successfully")
            else:
                logger.warning(f"⚠️  {name} deployment may have failed")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✓ DEPLOYMENT COMPLETE: {deployment_count}/{len(army_composition)} units deployed")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Strategy execution failed: {e}")
        return False
