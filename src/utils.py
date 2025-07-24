import math

def calculate_distance(pos1, pos2):
    """
    Calculates the Euclidean distance between two points (x, y).
    Args:
        pos1 (tuple): A tuple (x1, y1) representing the first position.
        pos2 (tuple): A tuple (x2, y2) representing the second position.
    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def is_within_range(user_pos, tower_pos, coverage_radius):
    """
    Checks if a user is within the coverage range of a tower.
    Args:
        user_pos (tuple): User's position (x, y).
        tower_pos (tuple): Tower's position (x, y).
        coverage_radius (float): The coverage radius of the tower.
    Returns:
        bool: True if the user is within range, False otherwise.
    """
    return calculate_distance(user_pos, tower_pos) <= coverage_radius

def is_overlapping(tower1_pos, tower1_radius, tower2_pos, tower2_radius):
    """
    Checks if the coverage areas of two towers overlap.
    Args:
        tower1_pos (tuple): Position of the first tower (x, y).
        tower1_radius (float): Coverage radius of the first tower.
        tower2_pos (tuple): Position of the second tower (x, y).
        tower2_radius (float): Coverage radius of the second tower.
    Returns:
        bool: True if coverage areas overlap, False otherwise.
    """
    distance = calculate_distance(tower1_pos, tower2_pos)
    return distance < (tower1_radius + tower2_radius)