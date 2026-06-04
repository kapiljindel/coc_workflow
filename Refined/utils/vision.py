"""
Vision Module
Image processing, template matching, OCR, and screenshot handling
"""

import cv2
import numpy as np
import pytesseract
import os
import time
import random
from typing import Tuple, Optional

from .logger import get_logger
from .adb_connector import get_device, take_screenshot
from config.constants import (
    TESSERACT_PATH,
    ASSETS_PATH,
    IMG_PATH,
    TEMPLATE_MATCH_THRESHOLD_HIGH,
    TEMPLATE_MATCH_THRESHOLD_DEFAULT,
    COORDINATE_RANDOMIZATION_MIN,
    COORDINATE_RANDOMIZATION_MAX,
    CLICK_DELAY_MIN,
    CLICK_DELAY_MAX,
    OCR_UPSCALE_FACTOR,
    OCR_PSM_MODE_LINE,
    DEBUG_MODE,
)

logger = get_logger(__name__)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Template cache to avoid reloading images
_TEMPLATE_CACHE = {}

def _load_template(image_name: str) -> Optional[np.ndarray]:
    """
    Load template image from cache or disk
    
    Args:
        image_name: Name of the template file
        
    Returns:
        Image array or None if not found
    """
    if image_name in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[image_name]
    
    template_path = os.path.join(ASSETS_PATH, image_name)
    
    if not os.path.exists(template_path):
        logger.warning(f"Template not found: {template_path}")
        return None
    
    template = cv2.imread(template_path)
    if template is not None:
        _TEMPLATE_CACHE[image_name] = template
    
    return template

def clear_template_cache() -> None:
    """Clear the template cache to free memory"""
    _TEMPLATE_CACHE.clear()
    logger.debug("Template cache cleared")

def get_current_screen() -> Optional[np.ndarray]:
    """
    Capture current screen from device
    
    Returns:
        Screenshot as CV2 image array or None on error
    """
    try:
        device = get_device()
        if device is None:
            logger.error("Device not connected")
            return None
        
        screen_bytes = take_screenshot()
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        
        return screen
        
    except Exception as e:
        logger.error(f"Failed to capture screen: {e}")
        return None

def find_and_click(image_name: str, threshold: float = TEMPLATE_MATCH_THRESHOLD_DEFAULT, 
                   click: bool = True) -> bool:
    """
    Find image on screen and optionally click it
    
    Args:
        image_name: Template image filename
        threshold: Confidence threshold (0-1)
        click: Whether to actually click (or just detect)
        
    Returns:
        True if found, False otherwise
    """
    try:
        screen = get_current_screen()
        if screen is None:
            return False
        
        template = _load_template(image_name)
        if template is None:
            return False
        
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            if click:
                h, w = template.shape[:-1]
                margin_x = max(1, int(w * 0.15))
                margin_y = max(1, int(h * 0.15))
                
                random_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
                random_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
                
                # Add random offset to avoid detection
                random_x += random.randint(COORDINATE_RANDOMIZATION_MIN, COORDINATE_RANDOMIZATION_MAX)
                random_y += random.randint(COORDINATE_RANDOMIZATION_MIN, COORDINATE_RANDOMIZATION_MAX)
                
                time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
                get_device().shell(f"input tap {random_x} {random_y}")
                logger.debug(f"Clicked {image_name} at ({random_x}, {random_y})")
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"find_and_click failed for {image_name}: {e}")
        return False

def find_and_click_in_region(image_name: str, region: Tuple[int, int, int, int], 
                             threshold: float = TEMPLATE_MATCH_THRESHOLD_DEFAULT, 
                             click: bool = True) -> bool:
    """
    Find and click within a specific screen region
    
    Args:
        image_name: Template image filename
        region: (y1, y2, x1, x2) region tuple
        threshold: Confidence threshold
        click: Whether to actually click
        
    Returns:
        True if found, False otherwise
    """
    try:
        screen = get_current_screen()
        if screen is None:
            return False
        
        y1, y2, x1, x2 = region
        cropped_screen = screen[y1:y2, x1:x2]
        
        template = _load_template(image_name)
        if template is None:
            return False
        
        result = cv2.matchTemplate(cropped_screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            if click:
                h, w = template.shape[:-1]
                margin_x = max(1, int(w * 0.15))
                margin_y = max(1, int(h * 0.15))
                
                random_crop_x = random.randint(max_loc[0] + margin_x, max_loc[0] + w - margin_x)
                random_crop_y = random.randint(max_loc[1] + margin_y, max_loc[1] + h - margin_y)
                
                final_x = x1 + random_crop_x
                final_y = y1 + random_crop_y
                
                time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
                get_device().shell(f"input tap {final_x} {final_y}")
                logger.debug(f"Clicked {image_name} in region at ({final_x}, {final_y})")
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"find_and_click_in_region failed: {e}")
        return False

def find_multiple_templates(template_names: list, screen: Optional[np.ndarray] = None,
                            threshold: float = TEMPLATE_MATCH_THRESHOLD_DEFAULT) -> Optional[Tuple[str, Tuple[int, int]]]:
    """
    Find best match among multiple templates
    
    Args:
        template_names: List of template filenames
        screen: Optional pre-captured screen
        threshold: Confidence threshold
        
    Returns:
        (template_name, (x, y)) or None if no match found
    """
    if screen is None:
        screen = get_current_screen()
    
    if screen is None:
        return None
    
    best_match = None
    best_score = 0
    
    for name in template_names:
        try:
            template = _load_template(name)
            if template is None:
                continue
            
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_match = (name, max_loc)
                best_score = max_val
        
        except Exception as e:
            logger.debug(f"Error matching {name}: {e}")
            continue
    
    if best_score >= threshold:
        return best_match
    
    return None

def _extract_number(screen: np.ndarray, region: Tuple[int, int, int, int], 
                    debug_filename: str, psm_mode: int = OCR_PSM_MODE_LINE) -> int:
    """
    Extract number from screen region using OCR
    
    Args:
        screen: Screen image array
        region: (y1, y2, x1, x2) crop region
        debug_filename: Filename to save debug image
        psm_mode: Tesseract PSM mode
        
    Returns:
        Extracted number or 0 if extraction failed
    """
    try:
        y1, y2, x1, x2 = region
        crop = screen[y1:y2, x1:x2]
        
        if crop.size == 0:
            return 0
        
        # Upscale and prepare
        bigger = cv2.resize(crop, None, fx=OCR_UPSCALE_FACTOR, fy=OCR_UPSCALE_FACTOR, 
                            interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Save debug image if enabled
        if DEBUG_MODE:
            os.makedirs(IMG_PATH, exist_ok=True)
            cv2.imwrite(os.path.join(IMG_PATH, debug_filename), thresh)
        
        # OCR extraction
        config_str = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789%'
        text = pytesseract.image_to_string(thresh, config=config_str)
        clean_text = ''.join(filter(str.isdigit, text))
        
        return int(clean_text) if clean_text else 0
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return 0

def read_loot(screen: Optional[np.ndarray] = None) -> Tuple[int, int]:
    """
    Read gold and elixir values from screen
    
    Args:
        screen: Optional pre-captured screen
        
    Returns:
        (gold, elixir) tuple
    """
    from config.constants import GOLD_REGION, ELIXIR_REGION
    
    if screen is None:
        screen = get_current_screen()
    
    if screen is None:
        return 0, 0
    
    gold = _extract_number(screen, GOLD_REGION, "debug_gold.png")
    elixir = _extract_number(screen, ELIXIR_REGION, "debug_elixir.png")
    
    return gold, elixir

def read_damage(screen: Optional[np.ndarray] = None) -> int:
    """
    Read damage percentage from screen
    
    Args:
        screen: Optional pre-captured screen
        
    Returns:
        Damage percentage
    """
    from config.constants import DAMAGE_REGION
    
    if screen is None:
        screen = get_current_screen()
    
    if screen is None:
        return 0
    
    return _extract_number(screen, DAMAGE_REGION, "debug_damage.png")

def read_troops(screen: Optional[np.ndarray] = None) -> int:
    """
    Read troop count from screen
    
    Args:
        screen: Optional pre-captured screen
        
    Returns:
        Troop count
    """
    from config.constants import TROOP_REGION
    
    if screen is None:
        screen = get_current_screen()
    
    if screen is None:
        return 0
    
    return _extract_number(screen, TROOP_REGION, "debug_troops.png")

def save_debug_screenshot(regions: Optional[dict] = None) -> bool:
    """
    Save debug screenshot with marked regions
    
    Args:
        regions: Dictionary of region_name: (y1, y2, x1, x2)
        
    Returns:
        True if successful
    """
    if not DEBUG_MODE:
        return False
    
    try:
        screen = get_current_screen()
        if screen is None:
            return False
        
        from config.constants import GOLD_REGION, ELIXIR_REGION, DAMAGE_REGION
        
        # Default regions if none provided
        if regions is None:
            regions = {
                "gold": GOLD_REGION,
                "elixir": ELIXIR_REGION,
                "damage": DAMAGE_REGION,
            }
        
        # Draw rectangles for all regions
        colors = {
            "gold": (0, 0, 255),        # Red
            "elixir": (255, 0, 255),    # Magenta
            "damage": (0, 255, 0),      # Green
        }
        
        for region_name, (y1, y2, x1, x2) in regions.items():
            color = colors.get(region_name, (255, 255, 255))
            cv2.rectangle(screen, (x1, y1), (x2, y2), color, 2)
            cv2.putText(screen, region_name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.4, color, 1)
        
        # Save screenshot
        os.makedirs(IMG_PATH, exist_ok=True)
        output_path = os.path.join(IMG_PATH, "debug_screenshot.png")
        cv2.imwrite(output_path, screen)
        logger.debug(f"Debug screenshot saved: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save debug screenshot: {e}")
        return False
