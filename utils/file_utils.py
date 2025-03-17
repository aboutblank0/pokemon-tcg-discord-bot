import re

def sanitize_filename(filename):
    """
    Removes or replaces invalid characters from a filename to make it safe for use in Windows and other OS.
    
    Invalid characters: \ / : * ? " < > |
    Replaces them with '_'.
    
    :param filename: Original filename as a string
    :return: Sanitized filename as a string
    """
    return re.sub(r'[\/:*?"<>|]', '_', filename)
