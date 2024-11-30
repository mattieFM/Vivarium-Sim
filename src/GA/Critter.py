from GA.Gene import Gene
from CORE.entity import Entity
import random

class Critter(Entity):
    critters = []
    
    """Class representing a critter in the simulation."""
    def __init__(self, base, city, position=(0, 0, 0), strength=1.0, color=None, genes=None):
        """
        Initialize a new critter.
        
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
            model="./assets/models/critter.obj"
            )

        self.city = city
        self.strength = strength
        self.color = color
        self.get_rand_color() #update if none
        
        self.genes = genes if genes is not None else [
            Gene("Strength", strength, min_value=0.5, max_value=2.0)
        ]  # Default to a strength gene
        
        self.fitness = 0  # Initialize fitness score
        self.base=base
        
    @staticmethod
    def remove_all_critters():
        Entity.remove_list_of_entities(Critter.critters)
        
    def spawn(self, x=None, y=None, color=None):
        if(self.base.valid_x_y(x,y)):
            critter = super().spawn(x, y, color)
            Critter.critters.append(critter)
            self.city.add_child(critter)
            return critter
    
    def remove(self):
        Entity.remove_entity_from_list(self,Critter.critters)
        return super().remove()
        
    def get_rand_color(self):
        from main import BaseApp
        if self.color is None:
            self.color = random.choice(BaseApp.CRITTER_COLORS)
        

    def move(self, new_x, new_y):
        """
        Update the critter's position.
        
        Args:
            new_x (float): New X-coordinate.
            new_y (float): New Y-coordinate.
        """
        self.position = (new_x, new_y, self.position[2])

    def adjust_fitness(self, amount):
        """
        Adjust the critter's fitness score.
        
        Args:
            amount (float): Amount to adjust fitness by (positive or negative).
        """
        self.fitness += amount

    def __str__(self):
        """Return a string representation of the critter for debugging."""
        return (f"Critter(ID={self.id}, Position={self.position}, Strength={self.strength}, "
                f"Color={self.color}, Fitness={self.fitness})")