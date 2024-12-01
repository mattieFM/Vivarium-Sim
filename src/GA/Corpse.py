from GA.Gene import Gene
from CORE.entity import Entity
import random

class Corpse(Entity):
    """Class representing a corpse in the simulation."""
    
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
        Initialize a new city.
        
        Args:
            position (tuple): Initial (x, y, z) position of the critter.
            strength (float): Ability to climb steep terrain.
            color (tuple): RGBA color representing the critter visually.
            genes (list or dict): List of Gene objects representing the critter's genetic makeup.
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
        Entity.remove_list_of_entities(Corpse.corpses)
        
    def spawn(self, x=None, y=None, color=None):
        if(self.base.valid_x_y(x,y)):
            corpse = super().spawn(x, y, color)
            Corpse.corpses.append(corpse)
            corpse.body_np.set_hpr(0,90,0)
            return corpse

    def remove(self):
        Entity.remove_entity_from_list(self,Corpse.corpses)
        return super().remove()
        

    def __str__(self):
        """Return a string representation of the critter for debugging."""
        return (f"Corpse(ID={self.id}, Position={self.position}, "
                f"Color={self.color})")