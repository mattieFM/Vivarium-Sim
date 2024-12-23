"""
This module defines the `Critter` class, representing a critter entity in the simulation.

The `Critter` class extends the `Entity` class and is responsible for simulating the behavior and
actions of critters within a city in the environment. It includes functionalities like seeking food,
evaluating fitness, fighting, and handling behaviors like cannibalism and targeting other critters.

This class interacts with other components such as `Food`, `Corpse`, and `City`, and includes methods 
for spawning, moving, eating, and resetting the critter's state during simulation rounds.

Example Usage:
    from simulation import Critter

    # Create a new critter in a city
    critter = Critter(base, city)
    critter.spawn(100, 200)
"""


from GA.Gene import Gene
from CORE.entity import Entity
from direct.task import Task
from panda3d.core import Vec3
from GA.Corpse import Corpse
import random
from GA.City import City
from GA.Food import Food
import numpy as np

class Critter(Entity):
    """
    Represents a critter in the simulation, extending from the `Entity` class.

    A `Critter` is an entity in the simulation that interacts with its environment by seeking food,
    fighting enemies, and aiming to survive. It has various behaviors that depend on its genes, including
    the ability to engage in cannibalism or target specific foods or critters.

    The critter can evaluate its fitness based on how much food it consumes, how quickly it consumes
    food, and whether it returns to the city. It can move to new locations, fight other critters, and
    spawn new critters.

    Attributes:
        critters (list): A list holding all active `Critter` objects in the simulation.
        city (City): The city to which this critter belongs.
        strength (float): The critter's ability to interact with the environment.
        color (tuple): RGBA color for the critter's visual appearance.
        fitness (float): The critter's current fitness score.
        got_food_this_round (bool): Whether the critter has eaten food in the current round.
        current_food_goal (Food): The food item the critter is currently targeting.
        seek_food_task (Task): A task for seeking food during the simulation.
        time_to_reach_first_food (float): Time taken to reach the first food in the simulation.
        out_for_a_fight (bool): Whether the critter is seeking a fight (i.e., targeting an enemy).
        at_city (bool): Whether the critter is currently at the city.
        returning_to_city (bool): Whether the critter is returning to the city after eating.
        out_for_cannibalism (bool): Whether the critter is engaging in cannibalistic behavior.

    Methods:
        evaluate(): Evaluates the critter's fitness based on its actions during the round.
        target_food(food): Sets the critter to target and move towards a piece of food.
        target_chosen_food(): Targets the food the critter has chosen to go after.
        closest_food_in_threshold(): Finds the closest food within a specified threshold.
        find_food(): Determines the next piece of food the critter will attempt to target.
        find_closest_food(): Finds and returns the closest food to the critter.
        target_nearest_food(): Finds and targets the nearest food.
        eat(): Causes the critter to spawn a corpse and consume food.
        consume_food(food): Eats a piece of food if it is not already eaten.
        is_full(): Determines whether the critter has eaten all it can eat.
        is_last_survivor(): Checks if the critter is the last survivor in the city.
        seek_food(): Initiates a task to seek food.
        task_seek_food(task): The task method to continuously search for food.
        consume_target_food_if_nearby(): Consumes the target food if it's nearby.
        consume_nearby_food(): Consumes one piece of food that is nearby.
        reset(): Resets the critter's state for the next simulation round.
        move_task(task): Moves the critter to a location and performs actions at the destination.
        remove_all_critters(): Removes all critters from the simulation.
        return_to_city(): Returns the critter to the home city.
        spawn(x, y, color): Spawns a new critter at the specified location with a given color.
        remove(): Removes the critter from the simulation and resets tasks.
        get_rand_color(): Randomly selects a color for the critter if none is provided.
        move(new_x, new_y): Updates the critter's position.
        adjust_fitness(amount): Adjusts the critter's fitness score.
        __str__(): Returns a string representation of the critter for debugging.
    """
    critters = []
    
    """Class representing a critter in the simulation."""
    def __init__(self, base, city, position=(0, 0, 0), strength=1.0, color=None, genes=None):
        """
        Initialize a new critter with a given position, strength, color, and genes.

        Args:
            position (tuple): Initial (x, y, z) position of the critter.
            strength (float): Ability to interact with the environment.
            color (tuple): RGBA color representing the critter visually.
            genes (list or dict): List or dictionary of `Gene` objects representing the critter's genetic makeup.
        """

        super().__init__(
            base=base,
            color=color,
            position=position,
            model="models/critter.obj",
            genes=genes
            )

        self.city = city
        self.strength = strength
        self.color = color
        self.get_rand_color() #update if none
        

        self.fitness = 0  # Initialize fitness score
        self.got_food_this_round = False
        self.base=base
        self.current_food_goal = None
        self.seek_food_task=None
        self.time_to_reach_first_food = np.inf
        
        #wether this critter is targeting an enemy
        self.out_for_a_fight = False
        
        self.at_city=False
        self.returning_to_city=False
        self.out_for_cannibalism=False
        
    def reset_seek_task(self):
        """remove the current seek food task """
        if(self.seek_food_task != None):
            self.base.taskMgr.remove(self.seek_food_task)
    
    def evaluate(self):
        """the fitness of the creature is defined as
            1 point if they eat any food
            + the amount of food they ate / the max they can eat
            + 2 points per enemy eaten (since a enemy is a food and an enemy and we give points for each)
            + 0-1 points based on how fast they got their food
            -1 point if it did not return home
            0 points if they did not eat. 
        """
        fit = 1 if self.got_food_this_round else 0
        fit += self.food_eaten / self.get_gene("Max Food")
        fit += self.enemiesEaten
        fit += self.time_to_reach_first_food/self.base.round_manager.phase_time_limit_seconds
        fit = fit if self.at_city else 0 #must have returned home otherwise 0 fitness
        self.fitness = fit
        return self.fitness
            
    def target_food(self,food):
        """
        Sets the critter to target a specific piece of food and move towards it.

        Args:
            food (Food): The food the critter is targeting.
        """
        if(food != None and hasattr(food, "get_pos")):
            pos = food.get_pos()
            if(pos[0]==0 and pos[1] == 0 and pos[2] == 0 ):
                self.return_to_city()
            else:
                self.current_food_goal = food
                self.move_to(pos)
        
    def target_chosen_food(self):
        """
        Determines the next piece of food the critter will attempt to target based on its position
        and genetic factors like cannibalism, closest food, and random food choices.

        Args:
            depth (int, optional): Recursion depth for handling eaten food. Defaults to 0.

        Returns:
            Food or None: The food the critter targets or None if no food is found.
        """

        target = self.find_food()
        
        if(target != None):
            self.target_food(target)
        
    def closest_food_in_threshold(self):
        """find the closest food within the gene closeness threshold
        if one is not found go to the closest one

        Returns:
            _type_: _description_
        """
        closestFood = None
        food_dist = np.inf
        for food in Food.foods:
            dist = self.distance(food)
            if(dist<self.get_gene("Close Threshold")):
                return food
            else:
                if(dist < food_dist):
                    closestFood = food
                    food_dist = dist
        return closestFood
        
    def find_food(self,depth=0):
        """
        Determines the next piece of food the critter will attempt to target based on its position
        and genetic factors like cannibalism, closest food, and random food choices.

        Args:
            depth (int, optional): Recursion depth for handling eaten food. Defaults to 0.

        Returns:
            Food or None: The food the critter targets or None if no food is found.
        """

        food = None      
        # print(f"round time: {self.base.round_manager.get_phase_time()}")
        # print(f"wait:{self.get_gene('Cannibalism Wait')}")
        if(self.get_gene("Cannibalism Chance") > random.random() and self.get_gene("Cannibalism Wait") < self.base.round_manager.get_phase_time()):
            # print("--Cannibal on the hunt--")
            random.shuffle(self.city.children)
            
            self.out_for_cannibalism = True
            
            if(self.get_gene("Smart Cannibalism") > random.random()):
                self.out_for_a_fight = False
                self.city.children.sort(key=lambda child: child.times_eaten)
            #print(self.city.children)
            
            food = self.city.children[0]
            if(food == self):
                self.out_for_a_fight = False
                food = None
        
        if(self.get_gene("Closest Food First") > random.random() and len(Food.foods) > 0):
            #target closest first
            self.out_for_a_fight = False
            food = self.find_closest_food()
        elif(self.get_gene("Eat Other Tribes Chance") > random.random() and not self.is_last_survivor()):
            # print("--Out for blood--")
            # print(self)
            # print("-- --")
            city = City.cities[random.randint(0,len(City.cities)-1)]
            i=0
            while city == self.city and i < 10:
                i+=1
                city = City.cities[random.randint(0,len(City.cities)-1)]
                
            #0 since this gets shuffled constantly
            
            if(len(city.children) > 0):
                self.out_for_a_fight = True
                random.shuffle(city.children)
                food = city.children[0]  
            
            if(i>10):
                food = None
                
        elif(self.get_gene("Random Food First") > random.random() and len(Food.foods) > 0):
            #random first
            random.shuffle(Food.foods)
            food = Food.foods[0]
        elif(food == None and len(Food.foods) > 0):
            self.out_for_a_fight = False
            food = self.closest_food_in_threshold()
        elif(food == None):
            self.move_to(Vec3(
                self.get_gene("x-nest-offset") + self.city.get_pos().getX(),
                self.get_gene("y-nest-offset") + self.city.get_pos().getY()
                ,0
                ))
            return None
            
            
        if(self.get_gene("Checks Eaten") > random.random() and food != None):
            if(food.eaten and depth < 100):
                food = self.find_food(depth=depth+1)
            
        return food
    
    def find_closest_food(self):
        """
            find the closeset food to this critter and return its Food obj
        """
        closest = None
        closest_dist = np.inf
        random.shuffle(Food.foods)
        for food in Food.foods:
            dist = self.distance(food)
            if(dist<closest_dist):
                closest=food
                closest_dist=dist
        return closest
        
    def target_nearest_food(self):
        """find and target the closest food"""
        closest = self.find_closest_food()
        
        self.target_food(closest)
        
    def eat(self):
        """extend eat function to spawn a corpse when eaten"""
        Corpse(self.base).spawn(self.get_pos().getX(),self.get_pos().getY())
        return super().eat()
        
    def consume_food(self,food):
        """eat a food, if the food is not eaten"""
        if(isinstance(food,Critter)):
            self.fight(food)
        else:
            can_eat = food.eat()
            if(can_eat):
                time_since_round_start = self.base.round_manager.get_phase_time()
                if(time_since_round_start < self.time_to_reach_first_food):
                    self.time_to_reach_first_food=time_since_round_start
                self.got_food_this_round=True
                self.food_eaten+=1
                if(self.food_eaten > self.get_gene("Max Food")):
                    self.food_eaten = self.get_gene("Max Food")
            
    def is_full(self):
        """has this critter eaten all it can eat?"""
        return self.food_eaten >= self.get_gene("Max Food")
    
    def is_last_survivor(self):
        """is this the last critter not at the city or alive"""
        sum(not child.eaten and not child.at_city for child in self.city.children) <= 1
    
    def seek_food(self):
        self.reset_seek_task()
        self.seek_food_task = self.base.task_mgr.add(self.task_seek_food, f"entity{self.id}-move-task-to-food")
        
    def task_seek_food(self, task):
        """a task to seek out the nearest food and eat it till this critter cannot eat/carry any more"""
        if(getattr(self.current_food_goal,"at_city",False)):
            self.current_food_goal=None
            self.reset_move_task()
            
        if(not self.is_full()):
            #if there is nothing to do return
            if(len(Food.foods) > 0 and self.is_last_survivor()):
                self.return_to_city()
                return
            
            #otherwise do things
            if(self.current_food_goal != None):
                if(self.current_food_goal.eaten):
                    self.target_chosen_food()
                else:
                    pass
            else:
                self.target_chosen_food()
                
            #chance to change mind
            if(self.get_gene("Change Mind Chance") < random.random()):
                self.returning_to_city = False
                self.target_chosen_food()
        else:
            self.return_to_city()
            
        return Task.cont
        
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
        if(self.food_eaten < self.get_gene("Max Food")):
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
        self.got_food_this_round = False
        self.food_eaten = 0
        self.enemiesEaten = 0
        self.current_food_goal = None
        self.time_to_reach_first_food = np.inf
        
        self.at_city=False
        self.returning_to_city=False
        
    def move_task(self, task):
        """a task to move the critter to a location overidden to eat food at the end of the path

        Args:
            task (_type_): _description_

        Returns:
            _type_: _description_
        """
        response = super().move_task(task)
        if(response == Task.done and self.returning_to_city):
            self.at_city = True
        elif(response == Task.done and self.out_for_a_fight):
            self.fight(self.current_food_goal)
        elif(response == Task.done and not self.returning_to_city):
            self.consume_target_food_if_nearby()

        
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
            critter = super().spawn(x, y, self.city.color)
            Critter.critters.append(critter)
            self.city.add_child(critter)
            return critter
    
    def remove(self):
        Entity.remove_entity_from_list(self,Critter.critters)
        self.reset_seek_task()
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
        return (f"Critter(Alive:{not self.eaten},Fitness:{self.fitness}at_city:{self.at_city},food_eaten={self.food_eaten}\n" +
                self.get_all_genes_as_str() +
                ")"
                
                )