class Util():
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