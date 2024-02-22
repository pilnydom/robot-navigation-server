def get_coordinates(message):
    """Get the coordinates from a message.
    
    Args:
        message (str): The message to get the coordinates from.
    """
    coordinates = message.split(" ")[1:3]
    return int(coordinates[0]), int(coordinates[1])

def coordinate_diff(prev_coord, curr_coord):
    """Takes two coordinates and returns the absolute difference between them.
    
    Args:
        prev_coord (int): The previous coordinate.
        curr_coord (int): The current coordinate
        
    Returns:
        int: The difference between the two coordinates.
    """
    return abs(int(curr_coord)) - abs(int(prev_coord))

def valid_syntax(string, lenght):
    """Check if a string has a valid syntax.
    
    Args:
        string (str): The string to check.
        lenght (int): The maximum length of the string.
    """
    return len(string) <= lenght and " " not in string

def is_positive_segment(x, y):
    """Check if a segment is positive.
    
    Args:
        x (int): The x coordinate.
        y (int): The y coordinate.
    """
    return x * y > 0