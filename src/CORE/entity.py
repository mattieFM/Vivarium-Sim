"""
This module defines the `Entity` class, which serves as the parent class for all movable and interactive entities 
within a 3D simulation world. Entities are capable of navigating the environment, interacting with other entities, 
and undergoing various behaviors influenced by genetic attributes.

The `Entity` class is built upon Panda3D's `DirectObject` framework and integrates physics interactions using 
the Bullet physics engine. Entities can have behaviors such as moving, fighting, eating, or spawning, and are 
governed by customizable genetic properties.

Classes:
    - `Entity`: Represents a generic interactive object or character in the simulation world.

Dependencies:
    - Panda3D's `DirectObject`, `Vec3`, and Bullet physics modules.
    - Genetic algorithm utilities from the `GA` package (e.g., `Gene`).
    - Utility functions from `CORE.util`.

Key Features:
    - Physics-enabled movement and collision detection.
    - Genetic-based behavior customization via `Gene` objects.
    - Pathfinding and movement tasks.
    - Interaction capabilities, such as eating, fighting, and color changes.
    - Static management of all entities within the simulation world.

Typical Usage Example:
    ```python
    from Entity import Entity

    base = SomeBaseAppInstance()  # Replace with your application instance
    entity = Entity(base, position=(10, 20, 0))
    entity.spawn()
    entity.move_to(Vec3(15, 25, 0))
    ```
"""


from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import Vec3
from GA.Gene import Gene
import numpy as np
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.bullet import BulletBoxShape,BulletRigidBodyNode
import random

from CORE.util import Util

class Entity(DirectObject):
    """the parent class of anything in the world that can move and interact"""
    entities = []
    
    def __init__(self, base, model="./assets/models/critter.obj", node=None,id=None,color=None,body_np=None,position=(0,0,0), genes=None):
        """the base entity class

        Args:
            base (BaseApp): _description_
            model (str, optional): the model to load for this entity. Defaults to "./assets/models/critter.obj".
            node (_type_, optional): if a node already exists?. Defaults to None.
            id (_type_, optional): _description_. Defaults to None.
            color (_type_, optional): the color (0,3,5,2). Defaults to None.
            body_np (_type_, optional): _description_. Defaults to None.
            position (tuple, optional): _description_. Defaults to (0,0,0).
        """
        super().__init__()
        self.base=base
        self.id = id
        self.color=color
        self.node=node
        self.body_np=body_np
        self.position = position
        self.spawned=False
        self.model=model
        self.speed=100 #default
        self.children = []
        self.move_task_ref = None
        self.can_be_eaten = True
        
        self.currentPath = [] #an array of the current path of vector3 nodes to follow
        self.currentDirection = (0,0,0)
        self.currentGoal = (0,0,0)
        
        self.food_eaten = 0
        self.enemiesEaten = 0
        
        self.genes = genes if genes is not None else [
            Gene("Strength", .5, min_value=0.5, max_value=2.0),
            
            Gene("Jump Strength", 1.1, min_value=1, max_value=5.0),
            Gene("Speed", 1.1, min_value=1, max_value=5.0),
            Gene("Jump Chance", .5, min_value=0, max_value=100),
            Gene("Random Motion Chance", 1, min_value=0, max_value=100),
            Gene("Random Motion -X Strength", .1, min_value=.1, max_value=10),
            Gene("Random Motion +X Strength", .1, min_value=.1, max_value=10),
            Gene("Random Motion -Y Strength", .1, min_value=.1, max_value=10),
            Gene("Random Motion +Y Strength", .1, min_value=.1, max_value=10),
            Gene("Random Motion -Z Strength", .1, min_value=.1, max_value=10),
            Gene("Random Motion +Z Strength", .1, min_value=.1, max_value=10),
            
            Gene("Max Food", .7, min_value=.7, max_value=10), # how much can this critter eat before they must return home
            Gene("Closest Food First", .5, min_value=0, max_value=1), #how often does this critter prioritize the closest food 
            Gene("Random Food First", .5, min_value=0, max_value=1), #how often does this critter prioritize the closest food 
            Gene("Checks Eaten", .5, min_value=0, max_value=1), #how often does this critter check if the food is eaten before deciding to go to it?
            Gene("Close Threshold", 30, min_value=10, max_value=500), # how far can a food be for this critter to be okay with it
            Gene("Change Mind Chance", .0001, min_value=0, max_value=.1, mutation_step=.0002), # how often does this critter change its mind on its goal?
        
            Gene("Eat Other Tribes Chance", .0001, min_value=0, max_value=1, mutation_step=.001), #how often does this critter try to eat enemies
        
            Gene("Cannibalism Chance", .0001, min_value=0, max_value=1, mutation_step=.001), # how often does this critter eat its allies
            Gene("Cannibalism Wait", 3, min_value=0, max_value=100, mutation_step=3), #on avg how long will they wait before turning to cannibalism
            Gene("Smart Cannibalism", .1, min_value=0, max_value=1, mutation_step=.01), # less likely to target critters with more food than it can carry
            
            
            Gene("x-nest-offset", 0, min_value=-200, max_value=200, mutation_step=100), # what offset from the nest does this critter like to wait at
            Gene("y-nest-offset", 0, min_value=-200, max_value=200, mutation_step=100), # what offset from the nest does this critter like to wait at
        ]  # Default to a strength gene
        
        self.apply_all_genes()
        self.eaten=False
        self.times_eaten = 0
        self.max_times_eaten = 1
        
    def eat(self):
        """simulate a critter eating this food
        
        return true if allowed to eat
        return false otherwise
        """
        from GA.Corpse import Corpse
        
        if(self.times_eaten >= self.max_times_eaten or not self.can_be_eaten):
            return False
        
        self.times_eaten+=1
        if(self.times_eaten >= self.max_times_eaten):
            self.eaten=True
            self.remove()
            
            
        return True
    
    @staticmethod
    def get_entities():
        """return all entities that have been spawned"""
        return Entity.entities
    
    @staticmethod
    def add_entity(entity):
        """add a entity to the global array of all entities

        Args:
            entity (Entity): the entity to add
        """
        Entity.entities.append(entity)
    
    @staticmethod
    def remove_entity(entity):
        """Remove an entity from the global array of all entities.

        Args:
            entity (Entity): The entity to remove
        """
        Entity.remove_entity_from_list(entity,Entity.entities)
            
    @staticmethod
    def remove_entity_from_list(entity,list):
        """Remove an entity from the global array of all entities.

        Args:
            entity (Entity): The entity to remove
        """
        try:
            list.remove(entity)
            #print(f"Entity {entity} removed successfully.")
        except ValueError:
            print(f"Entity {entity} not found in the list.")
    
    @staticmethod        
    def remove_list_of_entities(entities):
        """loop through a list of entities and remove each
        

        Args:
            entities (_type_): _description_
        """
        #TODO: refactor this it is bad
        i=0
        list_size = len(entities)
        while i in range(list_size):
            entity = entities[i]
            entity.remove()
            
            if(list_size != len(entities)):
                list_size=len(entities)
            else:
                i+=1
                
    def reset_move_task(self):
        """remove the current move task """
        if(self.move_task_ref != None):
            self.base.taskMgr.remove(self.move_task_ref)
                
    def move_to(self,vec3):
        """move from pos to target vec3 over s seconds

        Args:
            vec3 (vec3): vector3
        """
        pos = vec3
        if(hasattr(vec3,"get_pos")):
            pos = vec3.get_pos()
        
        self.currentGoal=Vec3(pos)
        self.reset_move_task()
        
        self.move_task_ref = self.base.task_mgr.add(self.move_task, f"entity{self.id}-move-task-to{vec3}")
        
    def distance(self,point):
        """get the 2d euclid distance between this and another point or entity"""
        self_pos = self.get_pos()
        other_pos = point
        if(hasattr(point,"get_pos")):
            other_pos=Vec3(point.get_pos())
        else:
            other_pos=Vec3(point)
        distance = np.linalg.norm(
            np.array([self_pos.getX(), self_pos.getY()]) -
            np.array([other_pos.getX(), other_pos.getY()])
        )
        return distance
            
    def get_all_genes_as_str(self):
        string = ""
        i=0
        for gene in self.genes:
            string += f"{gene.name}:{gene.value},"
            i+=1
            if(i % 3 == 0 ): string+="\n"
            
        return string
    def dist_to_point(self, point, threshold=5):
        """
        Check if a critter is within threshhold of point
    
        Args:
            food_pos (Vec3): Position of the goal point.
            threshold (float): Distance within which touching is detected.
    
        Returns:
            bool: True if within range, False otherwise.
        """
        try:
            distance = self.distance(point)
            return distance <= threshold
        except Exception as e:
            print(f"error in entity.dist_to_point:\n{e}")
            return False
        
    def move_task(self,task):
        if(not self.currentGoal or self.dist_to_point(self.currentGoal,20)):
            #reached goal
            self.currentGoal=None
            self.base.set_critter_height(self.body_np, self.get_pos().getX(), self.get_pos().getY())
            self.node.setLinearVelocity(Vec3(0, 0, .005))
            self.node.setAngularVelocity(Vec3(0, 0, 0))
            return Task.done
            
        else:
            #has not reached goal
            self.move_tick(self.currentGoal)
            return Task.cont
        
    def get_gene(self,name):
        """get the value of a gene via the name"""
        #get the value of the gene, but if we cant find it on this critter but it is requested anyways we will search the gene bank and give this 
        #critter the min value for that gene
        default = 0
        for gene in Gene.genes:
            if(gene.name == name):
                default = gene.min_value
                
        return getattr(self,name,default)
        
    def apply_all_genes(self):
        """propagate all gene changes to this critter"""
        for gene in self.genes:
            gene.apply(self)
        
    def move_tick(self,goal_point,extra_speed_mod=1,phys=True):
        from main import BaseApp
        direction = (goal_point - self.get_pos()).normalized()
        jump_strength = self.get_gene("Jump Strength")
        up_vector = Vec3(0,0,1)
        
        distance_to_move = self.get_gene("Speed") * self.speed * globalClock.getDt() * extra_speed_mod
        target_pos = Vec3(Vec3(self.get_pos()) + Vec3(direction*3))
        should_jump = False
        
        #check ahead to see if we need to jump via sampling
        linspace = np.linspace(.1,10,20)
        for value in linspace:
            target_pos = Vec3(self.get_pos()) + Vec3(direction*value)
            ahead_z_pos = self.base.terrainController.get_height_at(int(target_pos.getX()), int(target_pos.getY())) - self.base.terrainController.get_height_at(int(self.get_pos().getX()), int(self.get_pos().getY()))
            if ahead_z_pos > 0:
                should_jump=True
        
        
        z_difference = self.get_pos().getZ() - self.base.terrainController.get_height_at(int(self.get_pos().getX()), int(self.get_pos().getY()))
        
        #print(f"aheadz:{ahead_z_pos}")
        self.node.clear_forces()
        
        if(should_jump):
            #print("jump")
            #self.node.apply_central_impulse(up_vector*jump_strength)
            direction+=up_vector*jump_strength
        elif(z_difference > 30):
            #print("fall faster")
            direction+=-up_vector*jump_strength
            #self.node.apply_central_impulse()
            
        #random jumping to ensure no stuck
        if(random.randint(0,100) < self.get_gene("Jump Chance")):
            self.body_np.set_pos(self.get_pos()+Vec3(0,0,jump_strength))
            
        
            
        #cannot fall below 0
        pos = self.body_np.get_pos()
        pos[2]=Util.clamp(pos[2],0,999999)
        self.body_np.set_pos(pos)
        
        self.node.active=True
        
        #phys based movement or direct move?
        if(phys):
            self.node.apply_central_impulse(direction*distance_to_move)
            #print(f"random motion chance:{self.get_gene('Random Motion Chance')}")
            if(random.randint(0,100) < self.get_gene("Random Motion Chance")):
                #move random
                random_direction = Vec3(
                    random.uniform(-self.get_gene("Random Motion -X Strength"),self.get_gene("Random Motion +X Strength")),
                    random.uniform(-self.get_gene("Random Motion -Y Strength"),self.get_gene("Random Motion +Y Strength")),
                    random.uniform(-self.get_gene("Random Motion -Z Strength"),self.get_gene("Random Motion +Z Strength")),)
                self.node.setLinearVelocity(random_direction*distance_to_move*75)
            else:
                #move towards
                self.node.setLinearVelocity(direction*distance_to_move*75)
           
        else:
            new_pos = self.get_pos() + (direction*distance_to_move)
            #print(f"direction:{direction}.new_pos={new_pos}")
            self.body_np.set_pos(new_pos)
                
    def add_child(self,child):
        """add a child to the list of children

        Args:
            child (Entity): _description_
        """
        self.children.append(child)
    
    def remove_child(self, child):
        """remove a child if one exists from the list of children

        Args:
            child (Entity): _description_
        """
        self.remove_entity_from_list(child,self.children)
        
    def set_id(self,id=None):
        if(id==None): id = len(Entity.entities)
        self.id=id
        
    def remove(self):
        """Remove the spawned entity from the scene and physics world."""
        if not self.spawned:
            return  # If not spawned, nothing to remove
        
        self.reset_move_task()

        # Remove the entity's physics node from the physics world
        if self.node is not None:
            self.base.world.removeRigidBody(self.node)
            self.node = None

        # Detach the entity's NodePath from the scene graph
        if self.body_np is not None:
            self.body_np.removeNode()
            self.body_np = None

        # Clear additional references
        self.spawned = False
        self.position = (0,0,0)
        self.color = None

        # Remove from the entity list
        Entity.remove_entity(self)  # Assuming there's a method to manage entity cleanup
        self.spawned=False
        
    def update(self,x=None,y=None):
        self.remove()
        self.spawn(x,y)
        
    def eat_other(self,other):
        """have this critter eat another critter"""
        self.food_eaten+=.5
        if(getattr(self,"city",{}) != getattr(other,"city",[])):
            self.enemiesEaten+=.5
        other.eat()
        
        
    def change_color(self,color):
        """change the color of this entity

        Args:
            color (vector4): (r,g,b,a)
        """
        self.model.setColor(*color)
        
    def fight(self, other, random_chance=.01):
        """have this entity and another fight
        winner eats loser
        based on strength

        Args:
            other (entity): entity to fight
            random_chance (float, optional): random value (-this,this) added to results. Defaults to .01.
        Returns:
            true if self won false if other won
        
        """
        self_won=True
        if(other != None and not other.eaten and not getattr(other, "at_city",False)):
            print("murder")
            result = self.get_gene("Strength") - other.get_gene("Strength")
            result += random.uniform(-random_chance,random_chance)
            self_won = result > 0
            
            if(self_won):
                self.change_color((1,1,1,1))
                self.eat_other(other)
            else:
                self.change_color((1,0,0,1))
                other.eat_other(self)
        
        return self_won
        
    def get_pos(self):
        """get the (x,y,z) pos of this critter

        Returns:
            _type_: _description_
        """
        if(self.body_np != None):
            self.position = self.body_np.get_pos()
        return Vec3(self.position)
    
    def spawn(self, x=None, y=None, color=None):
        """a method to bring forth a phys enabled entity at chosen pos, height is automatic based on height map

        Args:
            x (float): _description_
            y (float): _description_
            color (tuple, optional): The color of the critter. Randomized if not provided.
        """
        from main import BaseApp
        
        if(self.node != None):
            self.node.setCcdMotionThreshold(0.1)  # Set threshold for continuous collision detection
            self.node.setCcdSweptSphereRadius(.1)
        
        if(x==None): x = self.position[0]
        if(y==None): y = self.position[1]
        if(color == None): color = self.color
        
        if(self.spawned): return self
        
        if(self.base.valid_x_y(x,y)):
        
            # Load the visual model for the critter
            blob = self.base.loader.loadModel(self.model)
            blob.setHpr(0, 0, 0)
            shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))

            # Create a BulletRigidBodyNode for physics
            self.set_id()
            node = BulletRigidBodyNode(f'Entity-{self.id}')

            # uhhh mass?
            node.setMass(1.0)
            node.addShape(shape)

            # Create phys ctrl ish, intermediate connected to real phys controller
            blob_np = self.base.render.attachNewNode(node)

            # lights??!?! idk
            blob.flattenLight()

            # Set parent to phys ctrl
            blob.reparentTo(blob_np)

            # Attach to the Bullet physics world
            self.base.world.attachRigidBody(node)

            # Adjust the critter's height based on the terrain
            z = self.base.set_critter_height(blob_np, x, y)
            blob_np.get_pos
            
            #self.critters.append((node,blob_np))
            blob.set_scale(10)

            # Assign a random color if none is provided
            if color is None:
                color = random.choice(BaseApp.CRITTER_COLORS)
                
            blob.setColor(*color)
            self.model = blob
            self.color = color
            self.node = node
            self.body_np = blob_np
            self.position=(x, y, z)
            self.spawned=True
            
            self.node.setAngularFactor(Vec3(0, 0, 0))

            # Create the critter instance and append to the critter list
            Entity.add_entity(self)
        
        return self
    
    