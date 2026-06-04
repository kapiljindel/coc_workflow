"""
Storage Module
Manages home village storage and loot tracking
"""

import cv2
import numpy as np
import os

from utils.vision import _extract_number
from utils.logger import get_logger
from utils.adb_connector import get_device
from config.constants import (
    HOME_GOLD_REGION,
    HOME_ELIXIR_REGION,
    MAX_GOLD,
    MAX_ELIXIR,
    IMG_PATH,
)

logger = get_logger(__name__)

def _capture_home_screen() -> np.ndarray:
    """Capture current home village screen"""
    device = get_device()
    if device is None:
        logger.error("Device not connected")
        return None
    
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    return screen

def check_home_loot() -> dict:
    """
    Check home village storage levels
    
    Returns:
        Dictionary with gold, elixir, and fill percentages
    """
    try:
        logger.info("Checking home village vaults...")
        
        screen = _capture_home_screen()
        if screen is None:
            return {"gold": 0, "elixir": 0, "gold_percent": 0, "elixir_percent": 0}
        
        # Extract values
        home_gold = _extract_number(screen, HOME_GOLD_REGION, "debug_home_gold.png")
        home_elixir = _extract_number(screen, HOME_ELIXIR_REGION, "debug_home_elixir.png")
        
        # Calculate percentages
        gold_percent = (home_gold / MAX_GOLD * 100) if MAX_GOLD > 0 else 0
        elixir_percent = (home_elixir / MAX_ELIXIR * 100) if MAX_ELIXIR > 0 else 0
        
        logger.info(f"Gold: {home_gold:,}/{MAX_GOLD:,} ({gold_percent:.1f}%)")
        logger.info(f"Elixir: {home_elixir:,}/{MAX_ELIXIR:,} ({elixir_percent:.1f}%)")
        
        result = {
            "gold": home_gold,
            "elixir": home_elixir,
            "gold_percent": gold_percent,
            "elixir_percent": elixir_percent,
            "needs_upgrade": gold_percent >= 90 or elixir_percent >= 90,
        }
        
        if result["needs_upgrade"]:
            logger.warning("⚠️  Storage nearly full! Consider upgrading walls or troops.")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to check home loot: {e}")
        return {"gold": 0, "elixir": 0, "gold_percent": 0, "elixir_percent": 0}

def get_loot_report() -> str:
    """Get formatted loot report for logging"""
    loot = check_home_loot()
    return (
        f"Home Storage: Gold {loot['gold']:,} ({loot['gold_percent']:.1f}%) | "
        f"Elixir {loot['elixir']:,} ({loot['elixir_percent']:.1f}%)"
    )
