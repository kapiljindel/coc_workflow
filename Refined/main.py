#!/usr/bin/env python3
"""
CoC Bot - Main Entry Point
Clash of Clans Automation Bot
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logging, get_logger
from utils.adb_connector import connect_device
from config.settings import get_config
from config.constants import ADB_HOST, ADB_PORT_DEFAULT, ADB_DEVICE_PORT_DEFAULT
from core.orchestrator import BotOrchestrator

logger = get_logger(__name__)

def main():
    """Main entry point"""
    try:
        # Setup logging
        setup_logging()
        logger.info("Initializing CoC Bot...")
        
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Extract ADB settings from config
        adb_port = config.get("ADB_PORT", ADB_DEVICE_PORT_DEFAULT)
        
        # Connect to device
        logger.info(f"Connecting to Android device on port {adb_port}...")
        connect_device(
            adb_host=ADB_HOST,
            adb_port=ADB_PORT_DEFAULT,
            device_port=adb_port
        )
        
        # Start orchestrator
        orchestrator = BotOrchestrator()
        orchestrator.run_forever()
        
    except KeyboardInterrupt:
        logger.info("\n\nBot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
