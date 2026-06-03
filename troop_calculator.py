import random

def calculate_bunches(total_troops):
    """
    Mathematically breaks the total army into random, unpredictable chunks.
    Returns a list of integers representing the number of troops per drop.
    """
    num_bunches = random.randint(4, 8)
    
    if total_troops <= 0: 
        return []
    if total_troops < num_bunches: 
        return [1] * total_troops 
        
    points = sorted(random.sample(range(1, total_troops), num_bunches - 1))
    bunches = [j - i for i, j in zip([0] + points, points + [total_troops])]
    
    random.shuffle(bunches) 
    return bunches