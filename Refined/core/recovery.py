"""
Recovery Module
Emergency recovery procedures for stuck bot states
"""

import time
import sys
import os

from utils.logger import get_logger
from utils.adb_connector import restart_app, get_device
from config.constants import APP_BOOT_TIME

logger = get_logger(__name__)

APP_PACKAGE = "com.supercell.clashofclans"

def rescue_bot():
    """
    Emergency bot recovery procedure
    
    1. Force stop the app
    2. Restart the app
    3. Wait for app to boot
    4. Reboot the Python bot
    """
    try:
        logger.error("\n" + "=" * 60)
        logger.error("🚨 EMERGENCY RECOVERY ACTIVATED")
        logger.error("=" * 60)
        
        # Force restart the app
        logger.info("Force restarting Clash of Clans...")
        try:
            restart_app(APP_PACKAGE)
            time.sleep(APP_BOOT_TIME)
        except Exception as e:
            logger.error(f"App restart failed: {e}")
        
        # Clear startup pop-ups (optional)
        device = get_device()
        if device:
            logger.info("Clearing welcome pop-ups...")
            for _ in range(3):
                device.shell("input tap 100 100")
                time.sleep(1)
        
        logger.info("🔄 Rebooting Python bot to resync with game...")
        time.sleep(2)
        
        # Restart the main script
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    except Exception as e:
        logger.error(f"Recovery failed: {e}")
        raise
