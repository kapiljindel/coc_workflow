"""
Deployment Module
Handles the actual deployment of troops to the battlefield
Refactored from deploy_swarm.py with better organization
"""

import time
import random
import cv2
import json
import os
from typing import List, Dict, Tuple

from utils.logger import get_logger
from utils.adb_connector import get_device
from utils.vision import find_and_click
from config.constants import (
    SPELL_PENETRATION_MIN,
    SPELL_PENETRATION_MAX,
    SPELL_OFFSET_MIN,
    SPELL_OFFSET_MAX,
    TROOP_POSITION_OFFSET_MIN,
    TROOP_POSITION_OFFSET_MAX,
    HOLD_TIME_PER_TROOP,
    HERO_TAP_COUNT_MIN,
    HERO_TAP_COUNT_MAX,
    CLEANUP_TAP_COUNT,
    IMG_PATH,
    DEBUG_MODE,
    STRATEGY_SINGLE_SIDE,
    STRATEGY_ALL_SIDES,
)

logger = get_logger(__name__)

def _load_deployment_strategy() -> str:
    """
    Load deployment strategy from config
    
    Returns:
        Deployment strategy name
    """
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
                return config.get("deploy_strategy", STRATEGY_SINGLE_SIDE)
    except:
        pass
    
    return STRATEGY_SINGLE_SIDE

def _get_deployment_points(all_side_points: Dict, strategy: str) -> List[Tuple[int, int]]:
    """
    Get deployment points based on strategy
    
    Args:
        all_side_points: Dictionary of side names to point lists
        strategy: Deployment strategy
        
    Returns:
        List of (x, y) coordinates
    """
    if strategy == STRATEGY_ALL_SIDES:
        # Surround the base from all sides
        safe_points = []
        for side_points in all_side_points.values():
            safe_points.extend(side_points)
        random.shuffle(safe_points)
        logger.info("Using ALL SIDES deployment strategy")
        return safe_points
    else:
        # Single side deployment
        chosen_side = random.choice(list(all_side_points.keys()))
        logger.info(f"Using SINGLE SIDE deployment on {chosen_side}")
        return all_side_points[chosen_side]

def _calculate_spell_drop_point(base_pt: Tuple[int, int], center: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calculate spell deployment point with penetration into base
    
    Args:
        base_pt: Edge deployment point
        center: Center of the base
        
    Returns:
        Adjusted deployment point
    """
    penetration = random.uniform(SPELL_PENETRATION_MIN, SPELL_PENETRATION_MAX)
    drop_x = int(base_pt[0] + (center[0] - base_pt[0]) * penetration)
    drop_y = int(base_pt[1] + (center[1] - base_pt[1]) * penetration)
    
    # Add random offset
    drop_x += random.randint(SPELL_OFFSET_MIN, SPELL_OFFSET_MAX)
    drop_y += random.randint(SPELL_OFFSET_MIN, SPELL_OFFSET_MAX)
    
    return drop_x, drop_y

def _calculate_troop_drop_point(base_pt: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calculate troop deployment point with small randomization
    
    Args:
        base_pt: Base deployment point
        
    Returns:
        Randomized point
    """
    drop_x = base_pt[0] + random.randint(TROOP_POSITION_OFFSET_MIN, TROOP_POSITION_OFFSET_MAX)
    drop_y = base_pt[1] + random.randint(TROOP_POSITION_OFFSET_MIN, TROOP_POSITION_OFFSET_MAX)
    
    return drop_x, drop_y

def _create_drop_coordinates(bunches: List[int], safe_points: List[Tuple[int, int]], 
                             category: str, center: Tuple[int, int]) -> List:
    """
    Create drop coordinates for all bunches
    
    Args:
        bunches: List of troop counts per bunch
        safe_points: Available deployment points
        category: Troop category (troop, spell, hero)
        center: Base center coordinates
        
    Returns:
        List of drop coordinates
    """
    final_drop_coords = []
    step = max(1, len(safe_points) / max(1, len(bunches)))
    
    for i in range(len(bunches)):
        if bunches[i] <= 0:
            final_drop_coords.append(None)
            continue
        
        pt_index = min(int(i * step), len(safe_points) - 1)
        base_pt = safe_points[pt_index]
        
        if category == "spell":
            drop_coords = _calculate_spell_drop_point(base_pt, center)
        else:
            drop_coords = _calculate_troop_drop_point(base_pt)
        
        final_drop_coords.append(drop_coords)
    
    return final_drop_coords

def _draw_debug_map(final_drop_coords: List, category: str) -> None:
    """
    Draw debug visualization of drop points
    
    Args:
        final_drop_coords: List of deployment coordinates
        category: Troop category
    """
    if not DEBUG_MODE or not os.path.exists(os.path.join(IMG_PATH, "tactical_map.png")):
        return
    
    try:
        debug_img = cv2.imread(os.path.join(IMG_PATH, "tactical_map.png"))
        if debug_img is None:
            return
        
        for coord in final_drop_coords:
            if coord is not None:
                dot_color = (255, 0, 255) if category == "spell" else (0, 255, 255)
                cv2.circle(debug_img, coord, 8, dot_color, -1)
                cv2.circle(debug_img, coord, 8, (0, 0, 0), 2)
        
        cv2.imwrite(os.path.join(IMG_PATH, "tactical_map.png"), debug_img)
        logger.debug("Debug map updated with deployment points")
    except Exception as e:
        logger.debug(f"Could not update debug map: {e}")

def _deploy_spells(troop_name: str, final_drop_coords: List) -> bool:
    """
    Deploy spell units
    
    Args:
        troop_name: Spell name
        final_drop_coords: List of drop coordinates
        
    Returns:
        True on success
    """
    device = get_device()
    if device is None:
        return False
    
    spell_commands = []
    for coord in final_drop_coords:
        if coord:
            dx, dy = coord
            spell_commands.append(f"input tap {dx} {dy}")
    
    if spell_commands:
        device.shell(" && sleep 0.01 && ".join(spell_commands))
    
    logger.info(f"✓ {troop_name} spells deployed")
    return True

def _deploy_heroes(troop_name: str, safe_points: List[Tuple[int, int]]) -> bool:
    """
    Deploy hero units
    
    Args:
        troop_name: Hero name
        safe_points: Available deployment points
        
    Returns:
        True on success
    """
    device = get_device()
    if device is None:
        return False
    
    tap_count = random.randint(HERO_TAP_COUNT_MIN, HERO_TAP_COUNT_MAX)
    tap_commands = []
    
    for _ in range(tap_count):
        random_pt = random.choice(safe_points)
        hx = random_pt[0] + random.randint(-15, 15)
        hy = random_pt[1] + random.randint(-15, 15)
        tap_commands.append(f"input tap {hx} {hy}")
    
    device.shell(" && sleep 0.01 && ".join(tap_commands))
    logger.info(f"✓ {troop_name} deployed ({tap_count} taps)")
    
    # 🎯 NEW: Activate hero ability after deployment
    try:
        time.sleep(random.uniform(0.5, 1.0))  # Wait for hero to land
        
        # Get hero slot and tap to activate ability
        from config.settings import get_config
        config = get_config()
        my_army = config.get("MY_ARMY", [])
        
        # Find the hero's slot in MY_ARMY
        for unit in my_army:
            if unit.get("name", "").lower() == troop_name.lower() and unit.get("category") == "hero":
                slot_name = unit.get("slot", "")
                if slot_name:
                    # Get slot coordinates
                    from tactics.troop_selection import get_army_slots
                    army_slots = get_army_slots()
                    if slot_name in army_slots:
                        y1, y2, x1, x2 = army_slots[slot_name]
                        ability_x = random.randint(x1 + 10, x2 - 10)
                        ability_y = random.randint(y1 + 10, y2 - 10)
                        device.shell(f"input tap {ability_x} {ability_y}")
                        logger.info(f"✓ {troop_name} ability ACTIVATED!")
                        time.sleep(random.uniform(0.2, 0.4))
                break
    except Exception as e:
        logger.warning(f"Could not activate {troop_name} ability: {e}")
    
    return True

def _deploy_regular_troops(bunches: List[int], safe_points: List[Tuple[int, int]], 
                           final_drop_coords: List) -> bool:
    """
    Deploy regular troop units
    
    Args:
        bunches: Troop counts per bunch
        safe_points: Available deployment points
        final_drop_coords: Drop coordinates
        
    Returns:
        True on success
    """
    device = get_device()
    if device is None:
        return False
    
    i = 0
    point_idx = 0
    
    while i < len(bunches):
        troops_to_drop = bunches[i]
        if troops_to_drop <= 0:
            i += 1
            continue
        
        # Split into deployable chunks
        troops_remaining = troops_to_drop
        commands = []
        
        while troops_remaining > 0:
            # Deploy 30-50 troops per swipe
            chunk = min(random.randint(30, 50), troops_remaining)
            troops_remaining -= chunk
            
            base_pt = safe_points[point_idx % len(safe_points)]
            point_idx += 1
            
            hx = base_pt[0] + random.randint(-15, 15)
            hy = base_pt[1] + random.randint(-15, 15)
            
            # Hold time based on chunk size (~40ms per troop)
            hold_time = chunk * HOLD_TIME_PER_TROOP
            
            commands.append(f"input swipe {hx} {hy} {hx} {hy} {hold_time}")
        
        # Execute all commands for this bunch
        device.shell(" && ".join(commands))
        i += 1
    
    # Cleanup taps
    cleanup_commands = []
    for _ in range(CLEANUP_TAP_COUNT):
        cleanup_pt = random.choice(safe_points)
        cleanup_commands.append(f"input tap {cleanup_pt[0]} {cleanup_pt[1]}")
    device.shell(" && ".join(cleanup_commands))
    
    logger.info("✓ Troops deployed")
    return True

def deploy_swarm(troop_name: str, category: str, bunches: List[int],
                  all_side_points: Dict, panic_points: List[Tuple[int, int]],
                  chosen_side_name: str) -> bool:
    """
    Deploy a troop type with specified bunches
    
    Args:
        troop_name: Name of troop to deploy
        category: Category (troop, spell, hero)
        bunches: List of deployment quantities
        all_side_points: Dictionary of tactical points
        panic_points: Backup deployment points
        chosen_side_name: Primary deployment side
        
    Returns:
        True if deployed successfully
    """
    try:
        total_dropping = sum(bunches)
        logger.info(f"Deploying {total_dropping}x {troop_name} ({category})")
        
        # Get deployment strategy and points
        strategy = _load_deployment_strategy()
        safe_points = _get_deployment_points(all_side_points, strategy)
        
        if not safe_points:
            safe_points = panic_points
        
        if not safe_points:
            logger.error("No deployment points available!")
            return False
        
        # Calculate base center
        all_x = [pt[0] for side in all_side_points.values() for pt in side]
        all_y = [pt[1] for side in all_side_points.values() for pt in side]
        center_x = sum(all_x) / len(all_x) if all_x else 500
        center_y = sum(all_y) / len(all_y) if all_y else 500
        center = (int(center_x), int(center_y))
        
        # Create drop coordinates
        final_drop_coords = _create_drop_coordinates(bunches, safe_points, category, center)
        _draw_debug_map(final_drop_coords, category)
        
        # Deploy based on category
        if category == "spell":
            return _deploy_spells(troop_name, final_drop_coords)
        elif category == "hero":
            return _deploy_heroes(troop_name, safe_points)
        else:  # regular troop
            return _deploy_regular_troops(bunches, safe_points, final_drop_coords)
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return False
