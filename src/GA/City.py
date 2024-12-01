"""
This module contains the definition of the `City` class, which represents a city in the simulation.

A city is the home of many critters and they evolve

The `City` class extends the `Entity` class and provides functionality for city creation, management,
and removal in the context of the simulation. It includes methods for spawning cities, managing their
bounds, and setting properties such as color and strength.

Example Usage:
    from simulation import City

    # Create a new city at a specific position
    city = City(base, position=(100, 200, 0))
    city.spawn(100, 200)
"""


from GA.Gene import Gene
from CORE.entity import Entity
import random

class City(Entity):
    """
    Represents a city in the simulation, inheriting from the `Entity` class.

    A city is an entity in the simulation with its own position, strength, and color. It can be spawned
    at specific coordinates and has a defined boundary radius. The `City` class provides functionality
    for city management, including spawning, getting bounds, removing, and setting the city color.

    Attributes:
        cities (list): A list holding all active `City` objects in the simulation.
        city_bounds_radius (float): The radius within which the city can influence the surrounding area.

    Methods:
        remove_all_cities(): Removes all cities from the simulation.
        spawn(x, y, color=None): Spawns a new city at the specified coordinates with the given color.
        get_bounds(): Returns the bounds of the city as a tuple (minX, maxX, minY, maxY).
        remove(): Removes the city from the simulation and its list of cities.
        get_rand_color(): Randomly assigns a color to the city if none is provided.
        __str__(): Returns a string representation of the city for debugging.
    """
    
    cities = []

    def __init__(self,
                 base,
                 position=(0, 0, 0),
                 strength=1.0,
                 color=None,
                 genes=None,
                 city_bounds_radius=50
                 ):
        """
        Initialize a new city with a position, strength, color, and genetic makeup.

        Args:
            position (tuple): Initial (x, y, z) position of the city.
            strength (float): Ability to influence or interact with terrain or entities.
            color (tuple, optional): RGBA color representing the city visually. Defaults to None.
            genes (list or dict, optional): List or dictionary of `Gene` objects representing the city's genetic makeup. Defaults to None.
            city_bounds_radius (float, optional): The radius within which the city has influence or interaction. Defaults to 50.
        """

        super().__init__(
            base=base,
            color=color,
            position=position,
            model="models/house.obj"
            )

        self.city_bounds_radius = city_bounds_radius
        self.get_rand_color() #update if none
        self.base=base
        self.can_be_eaten = False
        self.has_been_initialized = False
        
    @staticmethod
    def remove_all_cities():
        """
        Removes all cities from the simulation.

        This method clears the list of all active cities and removes them from the simulation.
        """
        Entity.remove_list_of_entities(City.cities)
        
    def spawn(self, x=None, y=None, color=None):
        """
        Spawns a new city at the specified (x, y) coordinates.

        Args:
            x (float, optional): The x-coordinate for the city's spawn location. Defaults to None.
            y (float, optional): The y-coordinate for the city's spawn location. Defaults to None.
            color (tuple, optional): RGBA color for the city's visual representation. Defaults to None.

        Returns:
            City: The newly spawned city instance.
        """

        if(self.base.valid_x_y(x,y)):
            city = super().spawn(x, y, color)
            City.cities.append(city)
            return city

    def get_bounds(self):
        """
        Returns the bounds of the city as a tuple (minX, maxX, minY, maxY).

        The bounds define the area around the city within the given `city_bounds_radius`.

        Returns:
            tuple: A tuple (minX, maxX, minY, maxY) representing the city's bounds.
        """

        pos = self.get_pos()
        x_center = pos[0]
        y_center = pos[1]
        
        x_min = x_center - self.city_bounds_radius
        x_max = x_center + self.city_bounds_radius
        
        y_min = y_center - self.city_bounds_radius
        y_max = y_center + self.city_bounds_radius
        
        return (x_min,x_max,y_min,y_max)
    
    def remove(self):
        """
        Removes the city from the simulation and from the list of cities.

        This method removes the city from the `City.cities` list and calls the `remove` method from the parent `Entity` class.

        Returns:
            bool: Returns the result of the `remove` method from the parent class, indicating if removal was successful.
        """

        Entity.remove_entity_from_list(self,City.cities)
        return super().remove()
        
    def get_rand_color(self):
        """
        Assigns a random color to the city if no color is provided.

        This method randomly selects a color from a predefined list of colors for the city.

        Returns:
            None
        """

        from main import BaseApp
        if self.color is None:
            self.color = random.choice(BaseApp.CRITTER_COLORS)

    def __str__(self):
        """
        Returns a string representation of the city for debugging purposes.

        Returns:
            str: A string in the format `City(ID=<ID>, Position=(<x>, <y>, <z>), Color=(<r>, <g>, <b>, <a>))`.
        """
        return (f"City(ID={self.id}, Position={self.position}, "
                f"Color={self.color})")