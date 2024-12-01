"""
This module defines the `Corpse` class, which represents a corpse in the simulation.

The `Corpse` class extends the `Entity` class and provides functionality for creating, managing,
and removing corpses in the simulation. It includes methods for spawning corpses, removing them,
and managing the list of all active corpses.

Example Usage:
    from simulation import Corpse

    # Create a new corpse at a specific position
    corpse = Corpse(base, position=(100, 200, 0))
    corpse.spawn(100, 200)
"""


from GA.Gene import Gene
from CORE.entity import Entity
import random

class Corpse(Entity):
    """
    Represents a corpse in the simulation, inheriting from the `Entity` class.

    A corpse is an entity in the simulation with its own position, color, and specific properties.
    It can be spawned at specific coordinates, removed from the simulation, and added to the list
    of active corpses. The `Corpse` class provides methods for spawning, removing, and managing the
    list of corpses.

    Attributes:
        corpses (list): A list holding all active `Corpse` objects in the simulation.

    Methods:
        remove_all_corpse(): Removes all corpses from the simulation.
        spawn(x, y, color=None): Spawns a new corpse at the specified coordinates with the given color.
        remove(): Removes the corpse from the simulation and its list of corpses.
        __str__(): Returns a string representation of the corpse for debugging.
    """
    
    corpses = []

    def __init__(self,
                 base,
                 position=(0, 0, 0),
                 strength=1.0,
                 color=(1,1,1,1),
                 genes=None,
                 city_bounds_radius=50
                 ):
        """
        Initialize a new corpse with a position, strength, color, and other properties.

        Args:
            position (tuple): Initial (x, y, z) position of the corpse.
            strength (float): Ability to interact with or influence other entities in the simulation.
            color (tuple, optional): RGBA color representing the corpse visually. Defaults to (1, 1, 1, 1).
            genes (list or dict, optional): List or dictionary of `Gene` objects representing the corpse's genetic makeup. Defaults to None.
            city_bounds_radius (float, optional): The radius within which the corpse has influence or interaction. Defaults to 50.
        """
        super().__init__(
            base=base,
            color=(1,0,0,1),
            position=position,
            model="./assets/models/critter.obj",
            )

        self.base=base
        self.can_be_eaten = False
        
    @staticmethod
    def remove_all_corpse():
        """
        Removes all corpses from the simulation.

        This method clears the list of all active corpses and removes them from the simulation.
        """

        Entity.remove_list_of_entities(Corpse.corpses)
        
    def spawn(self, x=None, y=None, color=None):
        """
        Spawns a new corpse at the specified (x, y) coordinates.

        Args:
            x (float, optional): The x-coordinate for the corpse's spawn location. Defaults to None.
            y (float, optional): The y-coordinate for the corpse's spawn location. Defaults to None.
            color (tuple, optional): RGBA color for the corpse's visual representation. Defaults to None.

        Returns:
            Corpse: The newly spawned corpse instance.
        """

        if(self.base.valid_x_y(x,y)):
            corpse = super().spawn(x, y, color)
            Corpse.corpses.append(corpse)
            corpse.body_np.set_hpr(0,90,0)
            return corpse

    def remove(self):
        """
        Removes the corpse from the simulation and from the list of corpses.

        This method removes the corpse from the `Corpse.corpses` list and calls the `remove` method from the parent `Entity` class.

        Returns:
            bool: Returns the result of the `remove` method from the parent class, indicating if removal was successful.
        """

        Entity.remove_entity_from_list(self,Corpse.corpses)
        return super().remove()
        

    def __str__(self):
        """
        Returns a string representation of the corpse for debugging purposes.

        Returns:
            str: A string in the format `Corpse(ID=<ID>, Position=(<x>, <y>, <z>), Color=(<r>, <g>, <b>, <a>))`.
        """

        return (f"Corpse(ID={self.id}, Position={self.position}, "
                f"Color={self.color})")