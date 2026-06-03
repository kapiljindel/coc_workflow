import random

def calculate_bunches(total_troops):
    """
    Mathematically breaks the total army into random, unpredictable chunks.
    Returns a list of integers representing the number of troops per drop.
    """
    # Decide how many spots to tap (between 4 and 8)
    num_bunches = random.randint(4, 8)
    
    if total_troops <= 0: 
        return []
    if total_troops < num_bunches: 
        return [1] * total_troops 
        
    # 'Stick breaking' math to divide the total into pieces
    points = sorted(random.sample(range(1, total_troops), num_bunches - 1))
    bunches = [j - i for i, j in zip([0] + points, points + [total_troops])]
    
    # Shuffle so the biggest chunk isn't always at the end
    random.shuffle(bunches) 
    return bunches