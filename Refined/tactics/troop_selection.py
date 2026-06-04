"""
Troop Selection Module
Selects specific troops from the army bar
"""

import time
import random

from utils.logger import get_logger
from utils.adb_connector import get_device
from config.constants import (
    CLICK_DELAY_MIN,
    CLICK_DELAY_MAX,
)

logger = get_logger(__name__)

def get_army_slots() -> dict:
    """
    Get army slot coordinates from configuration
    
    Returns:
        Dictionary mapping slot names to (y1, y2, x1, x2) coordinates
    """
    from config.settings import get_config
    try:
        config = get_config()
        return _generate_army_slots(config.get("MY_ARMY", []))
    except:
        logger.warning("Could not load army slots from config")
        return {}

def _generate_army_slots(my_army: list) -> dict:
    """
    Generate slot coordinates based on army composition
    
    Args:
        my_army: Army composition list from config
        
    Returns:
        Dictionary of slot coordinates
    """
    slots = {}
    y1, y2 = 745, 883
    current_x = 123
    box_width = 112
    
    for i, unit in enumerate(my_army):
        slot_name = f"slot_{i+1}"
        unit["slot"] = slot_name
        
        x1 = int(current_x)
        x2 = int(current_x + box_width)
        slots[slot_name] = (y1, y2, x1, x2)
        
        if i < len(my_army) - 1:
            curr_cat = unit.get("category", "troop")
            next_cat = my_army[i + 1].get("category", "troop")
            
            if curr_cat == next_cat:
                current_x = x2 + 10
            else:
                current_x = x2 + 26
    
    return slots

def select_troop(troop_name: str, slot_name: str) -> bool:
    """
    Select a troop from the army bar
    
    Args:
        troop_name: Name of the troop to select
        slot_name: Slot identifier (e.g., "slot_1")
        
    Returns:
        True on success
    """
    try:
        logger.debug(f"Selecting {troop_name} from {slot_name}...")
        
        # Get army slots
        army_slots = get_army_slots()
        
        if slot_name not in army_slots:
            logger.error(f"Slot {slot_name} not found in army configuration!")
            return False
        
        device = get_device()
        if device is None:
            logger.error("Device not connected")
            return False
        
        # Get random point in slot
        y1, y2, x1, x2 = army_slots[slot_name]
        tap_x = random.randint(x1 + 10, x2 - 10)
        tap_y = random.randint(y1 + 10, y2 - 10)
        
        # Tap the slot
        device.shell(f"input tap {tap_x} {tap_y}")
        time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
        
        logger.debug(f"✓ Selected {troop_name}")
        return True
        
    except Exception as e:
        logger.error(f"Troop selection failed: {e}")
        return False
