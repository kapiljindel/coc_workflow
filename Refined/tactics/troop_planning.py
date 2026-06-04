"""
Troop Planning Module
Calculates troop deployment bunches for unpredictable patterns
"""

import random
from utils.logger import get_logger
from config.constants import MIN_BUNCHES, MAX_BUNCHES

logger = get_logger(__name__)

def calculate_bunches(total_troops: int) -> list:
    """
    Break total troops into random, unpredictable bunches
    
    This creates varying-sized groups to avoid detection by anti-bot systems.
    Instead of deploying troops in a predictable pattern, we randomize the
    deployment chunks.
    
    Args:
        total_troops: Total number of troops to deploy
        
    Returns:
        List of integers representing troops per deployment
        
    Example:
        calculate_bunches(30) might return [5, 2, 8, 3, 12]
    """
    if total_troops <= 0:
        return []
    
    # Determine number of bunches (random between MIN and MAX)
    num_bunches = random.randint(MIN_BUNCHES, MAX_BUNCHES)
    
    # If fewer troops than bunches, return one troop per bunch
    if total_troops < num_bunches:
        return [1] * total_troops
    
    # Generate random split points
    split_points = sorted(random.sample(range(1, total_troops), min(num_bunches - 1, total_troops - 1)))
    
    # Create bunches from split points
    bunches = []
    prev = 0
    for point in split_points:
        bunches.append(point - prev)
        prev = point
    bunches.append(total_troops - prev)
    
    # Shuffle bunches for unpredictability
    random.shuffle(bunches)
    
    logger.debug(f"Split {total_troops} troops into {len(bunches)} bunches: {bunches}")
    return bunches
