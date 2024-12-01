"""
This module provides utility functions for common operations, such as clamping a value within a specified range.

Functions:
- clamp(value, minimum, maximum): Clamps a given value between a minimum and maximum bound.

Example Usage:
    from util import Util

    clamped_value = Util.clamp(10, 0, 5)  # Result: 5
"""


class Util():
    """
    A utility class providing static helper methods for various operations.

    This class contains only static methods and does not require instantiation. It is designed to
    offer utility functions that can be called directly from the class.

    Methods:
        clamp(value, minimum, maximum): Clamps a given value within a specified range.
    """
    @staticmethod
    def clamp(value, minimum, maximum):
        """Clamps the value between the minimum and maximum values. 

        Args:
            value (float): the value to clamp
            minimum (float): the minimum value allowed
            maximum (float): the max value allowed

        Returns:
            float: the new clamped value
        """
        return max(minimum, min(value, maximum))