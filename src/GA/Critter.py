from GA.Gene import Gene
from CORE.entity import Entity
from direct.task import Task
import random
from GA.Food import Food

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
            Gene("Strength", .5, min_value=0.5, max_value=2.0),
            Gene("Jump Chance", .5, min_value=0, max_value=100),
            Gene("Jump Strength", 1.1, min_value=1, max_value=5.0),
        ]  # Default to a strength gene
        
        
        self.fitness = 0  # Initialize fitness score
        self.got_food_this_round = False
        self.food_eaten = 0
        self.max_food = 1
        self.base=base
        self.current_food_goal = None
        
        self.at_city=False
        self.returning_to_city=False
    
    def target_food(self,food):
        """set critter to target a peice of food and move towards it"""
        self.current_food_goal = food
        self.move_to(food.get_pos())
        
    def consume_food(self,food):
        """eat a food, no checks, just eat"""
        self.got_food_this_round=True
        self.food_eaten+=1
        food.remove()
        
    def consume_target_food_if_nearby(self):
        """consume the target food if nearby it, if no target do nothing

        Returns:
            bool: did the food get eaten
        """
        found_food_near = False
        if(self.current_food_goal != None):
            if(self.dist_to_point(self.current_food_goal.get_pos()),20):
                    found_food_near=True
                    self.consume_food(self.current_food_goal)
        return found_food_near
                    
            
        
    def consume_nearby_food(self):
        """consume one piece of nearby food

        Returns:
            bool: did any food get eaten
        """
        found_food_near = False
        if(self.food_eaten < self.max_food):
            for food in Food.foods:
                if(self.dist_to_point(food.get_pos()),20):
                    found_food_near=True
                    self.consume_food(food)
                    break
        return found_food_near
        
    def reset(self):
        """reset any applicable things
        """
        self.got_food_this_round = False
        self.fitness = 0
        
    def move_task(self, task):
        """a task to move the critter to a location overidden to eat food at the end of the path

        Args:
            task (_type_): _description_

        Returns:
            _type_: _description_
        """
        response = super().move_task(task)
        if(response == Task.done):
            self.consume_target_food_if_nearby()
            
        if(response == Task.done and self.returning_to_city):
            self.at_city = True
        
        return response
        
    @staticmethod
    def remove_all_critters():
        Entity.remove_list_of_entities(Critter.critters)
        
    def return_to_city(self):
        """return to the home city
        """
        self.returning_to_city=True
        self.move_to(self.city)
        
    def spawn(self, x=None, y=None, color=None):
        """spawn one critter

        Args:
            x (_type_, optional): _description_. Defaults to None.
            y (_type_, optional): _description_. Defaults to None.
            color (_type_, optional): _description_. Defaults to None.

        Returns:
            Critter: Critter
        """
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