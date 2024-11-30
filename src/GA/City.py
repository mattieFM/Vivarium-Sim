from GA.Gene import Gene
from CORE.entity import Entity
import random

class City(Entity):
    """Class representing a city in the simulation."""
    
    cities = []

    def __init__(self, base, position=(0, 0, 0), strength=1.0, color=None, genes=None):
        """
        Initialize a new city.
        
        Args:
            position (tuple): Initial (x, y, z) position of the critter.
            strength (float): Ability to climb steep terrain.
            color (tuple): RGBA color representing the critter visually.
            genes (list or dict): List of Gene objects representing the critter's genetic makeup.
        """
        super().__init__(
            base=base,
            color=color,
            position=position,
            model="./assets/models/house.obj"
            )

        self.get_rand_color() #update if none
        self.base=base
        
    def spawn(self, x=None, y=None, color=None):
        city = super().spawn(x, y, color)
        City.cities.append(city)
        return city
        
    def get_rand_color(self):
        from main import BaseApp
        if self.color is None:
            self.color = random.choice(BaseApp.CRITTER_COLORS)

    def __str__(self):
        """Return a string representation of the critter for debugging."""
        return (f"Food(ID={self.id}, Position={self.position}, Strength={self.strength}, "
                f"Color={self.color}, Fitness={self.fitness})")