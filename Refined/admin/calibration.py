"""
Calibration and Testing Module
Tools for calibrating UI coordinates and testing bot functionality
"""

import cv2
from utils.vision import get_current_screen, save_debug_screenshot
from utils.logger import get_logger

logger = get_logger(__name__)

def calibrate_ui_boxes():
    """
    Capture and save calibration screenshot with all UI regions marked
    """
    logger.info("Capturing calibration screenshot...")
    save_debug_screenshot()
    logger.info("✓ Calibration screenshot saved to img/debug_screenshot.png")
    logger.info("Review this to verify all regions are correctly marked")

def test_template_matching():
    """
    Test template matching on current screen
    """
    from utils.vision import find_and_click
    
    logger.info("Testing template matching...")
    
    test_templates = [
        "main_attack.png",
        "find_match.png",
        "single_player_attack.png",
    ]
    
    for template in test_templates:
        result = find_and_click(template, click=False)
        logger.info(f"  {template}: {'✓ FOUND' if result else '✗ NOT FOUND'}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "calibrate":
            calibrate_ui_boxes()
        elif sys.argv[1] == "test":
            test_template_matching()
