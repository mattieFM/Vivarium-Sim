from GA.Gene import Gene
from CORE.entity import Entity
import random

class City(Entity):
    """Class representing a city in the simulation."""
    
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

        self.city_bounds_radius = city_bounds_radius
        self.get_rand_color() #update if none
        self.base=base
        
    @staticmethod
    def remove_all_cities():
        Entity.remove_list_of_entities(City.cities)
        
    def spawn(self, x=None, y=None, color=None):
        if(self.base.valid_x_y(x,y)):
            city = super().spawn(x, y, color)
            City.cities.append(city)
            return city

    def get_bounds(self):
        """get the bounds of this city in the form (minX,maxX,minY,maxY)"""
        pos = self.get_pos()
        x_center = pos[0]
        y_center = pos[1]
        
        x_min = x_center - self.city_bounds_radius
        x_max = x_center + self.city_bounds_radius
        
        y_min = y_center - self.city_bounds_radius
        y_max = y_center + self.city_bounds_radius
        
        return (x_min,x_max,y_min,y_max)
    
    def remove(self):
        Entity.remove_entity_from_list(self,City.cities)
        return super().remove()
        
    def get_rand_color(self):
        from main import BaseApp
        if self.color is None:
            self.color = random.choice(BaseApp.CRITTER_COLORS)

    def __str__(self):
        """Return a string representation of the critter for debugging."""
        return (f"City(ID={self.id}, Position={self.position}, "
                f"Color={self.color})")