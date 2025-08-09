# utils.py (or in a utilities file)
from django.contrib.auth.models import User

def is_user_in_group(user, group_name):
    """
    Checks if a user belongs to a specific group
    
    Args:
        user (User): The user to check
        group_name (str): The name of the group to check for
    
    Returns:
        bool: True if the user is in the group, False otherwise
    """
    return user.groups.filter(name=group_name).exists()