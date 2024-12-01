"""
This module contains the definition for the Food class in the simulation.

The Food class represents a food entity within the simulation world. It is inherited from the 
Entity class and includes methods for spawning, removing, and managing food entities. The 
Food class also interacts with the simulation environment, being a target for other entities 
like critters to seek out and consume.

Classes:
    Food (Entity): Represents a food object in the simulation.
"""


from GA.Gene import Gene
from CORE.entity import Entity
import random

class Food(Entity):
    """
    Class representing a food entity in the simulation.

    The Food class is responsible for managing food entities in the simulation. Each food 
    object has a position, color, and can be interacted with by critters in the environment. 
    It also includes methods to spawn and remove food, and ensure that each food item has a 
    randomly assigned color.

    Attributes:
        foods (list): A class-level list holding all food entities in the simulation.

    Methods:
        __init__(base, position=(0, 0, 0), strength=1.0, color=None, genes=None): 
            Initializes a new food entity with the given parameters.
        
        remove_all_food(): Removes all food entities from the simulation.
        
        spawn(x=None, y=None, color=None): Spawns a new food entity at the specified position.
        
        remove(): Removes the current food entity from the simulation.
        
        get_rand_color(): Assigns a random color to the food if no color is provided.
        
        __str__(): Returns a string representation of the food for debugging purposes.
    """
    
    foods = []

    def __init__(self, base, position=(0, 0, 0), strength=1.0, color=None, genes=None):
        """
        Initialize a new food.
        
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
            model="models/cube.obj"
            )

        self.get_rand_color() #update if none
        self.base=base
    
    @staticmethod
    def remove_all_food():
        Entity.remove_list_of_entities(Food.foods)
        
    def spawn(self, x=None, y=None, color=None):
        food = super().spawn(x, y, color)
        Food.foods.append(food)
        return food

    def remove(self):
        Entity.remove_entity_from_list(self,Food.foods)
        return super().remove()
        
    def get_rand_color(self):
        from main import BaseApp
        if self.color is None:
            self.color = random.choice(BaseApp.CRITTER_COLORS)

    def __str__(self):
        """Return a string representation of the critter for debugging."""
        return (f"Food(ID={self.id}, Position={self.position},  "
                f"Color={self.color})")