"""
Base Analysis Module
Analyzes base layout and generates tactical deployment points
"""

import cv2
import numpy as np
import os

from utils.logger import get_logger
from config.constants import (
    RED_THRESHOLD_MIN,
    RED_G_DIFF,
    RED_B_DIFF,
    BASE_BLOB_KERNEL_SIZE,
    BASE_BLOB_DILATION_ITERATIONS,
    TACTICAL_POINTS_PER_SIDE,
    IMG_PATH,
    DEBUG_MODE,
)

logger = get_logger(__name__)

# Tactical boundary configuration - these coordinates define deployment lines
LINE_TL_START = (164, 420)
LINE_TL_END = (665, 61)

LINE_TR_START = (978, 78)
LINE_TR_END = (1419, 400)

LINE_BR_START = (1070, 711)
LINE_BR_END = (1437, 422)

LINE_BL_START = (129, 432)
LINE_BL_END = (495, 700)

def _generate_line_points(pt1: tuple, pt2: tuple, num_points: int = TACTICAL_POINTS_PER_SIDE) -> list:
    """
    Generate evenly spaced points along a line
    
    Args:
        pt1: Starting point
        pt2: Ending point
        num_points: Number of points to generate
        
    Returns:
        List of (x, y) points
    """
    return [
        (int(pt1[0] + (pt2[0] - pt1[0]) * p), int(pt1[1] + (pt2[1] - pt1[1]) * p))
        for p in np.linspace(0, 1, num_points)
    ]

def get_safe_spam_points(screen_bytes: bytes) -> tuple:
    """
    Generate safe deployment points around base perimeter
    
    Args:
        screen_bytes: Screenshot bytes from device
        
    Returns:
        (all_side_points, panic_points) tuple
    """
    try:
        # Decode screenshot
        screen_arr = np.frombuffer(screen_bytes, np.uint8)
        screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
        h, w = screen.shape[:2]
        
        # Generate tactical points for each side
        all_side_points = {
            "Top-Left": _generate_line_points(LINE_TL_START, LINE_TL_END),
            "Top-Right": _generate_line_points(LINE_TR_START, LINE_TR_END),
            "Bottom-Right": _generate_line_points(LINE_BR_START, LINE_BR_END),
            "Bottom-Left": _generate_line_points(LINE_BL_START, LINE_BL_END),
        }
        
        # Panic points (backup deployment locations)
        panic_points = []
        for points in all_side_points.values():
            panic_points.extend(points)
        
        # Detect base (red mask detection)
        b = screen[:, :, 0].astype(np.int16)
        g = screen[:, :, 1].astype(np.int16)
        r = screen[:, :, 2].astype(np.int16)
        
        red_condition = (r > RED_THRESHOLD_MIN) & (r > g + RED_G_DIFF) & (r > b + RED_B_DIFF)
        red_mask = np.zeros((h, w), dtype=np.uint8)
        red_mask[red_condition] = 255
        
        kernel = np.ones((BASE_BLOB_KERNEL_SIZE, BASE_BLOB_KERNEL_SIZE), np.uint8)
        base_blob = cv2.dilate(red_mask, kernel, iterations=BASE_BLOB_DILATION_ITERATIONS)
        
        # Debug visualization
        if DEBUG_MODE:
            debug_screen = screen.copy()
            
            # Draw base detection
            colored_mask = np.zeros_like(screen)
            colored_mask[base_blob > 0] = [255, 0, 0]
            cv2.addWeighted(colored_mask, 0.3, debug_screen, 1.0, 0, debug_screen)
            
            # Draw tactical lines and points
            colors = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0)]
            for idx, (side_name, points) in enumerate(all_side_points.items()):
                color = colors[idx % len(colors)]
                
                # Draw line
                cv2.line(debug_screen, points[0], points[-1], color, 2)
                
                # Draw deployment points
                for point in points:
                    cv2.circle(debug_screen, point, 5, color, -1)
            
            # Draw panic points slightly different
            for point in panic_points:
                cv2.circle(debug_screen, point, 3, (0, 165, 255), -1)
            
            # Save debug image
            os.makedirs(IMG_PATH, exist_ok=True)
            cv2.imwrite(os.path.join(IMG_PATH, "tactical_map.png"), debug_screen)
            logger.debug(f"Tactical map saved to {IMG_PATH}/tactical_map.png")
        
        logger.info(f"✓ Generated {sum(len(p) for p in all_side_points.values())} tactical points")
        return all_side_points, panic_points
        
    except Exception as e:
        logger.error(f"Base scan failed: {e}")
        return {}, []
