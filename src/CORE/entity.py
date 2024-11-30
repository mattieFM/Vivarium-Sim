from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import Vec3
from panda3d.bullet import BulletBoxShape,BulletRigidBodyNode
import random

class Entity(DirectObject):
    """the parent class of anything in the world that can move and interact"""
    entities = []
    
    def __init__(self, base, model="./assets/models/critter.obj", node=None,id=None,color=None,body_np=None,position=(0,0,0)):
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
        
    def set_id(self,id=None):
        if(id==None): id = len(Entity.entities)
        self.id=id
    
    def spawn(self, x=None, y=None, color=None):
        """a method to bring forth a phys enabled entity at chosen pos, height is automatic based on height map

        Args:
            x (float): _description_
            y (float): _description_
            color (tuple, optional): The color of the critter. Randomized if not provided.
        """
        from main import BaseApp
        
        if(x==None): x = self.position[0]
        if(y==None): y = self.position[1]
        if(color == None): color = self.color
        
        if(self.spawned): return self
        
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
        
        self.color = color
        self.node = node
        self.body_np = blob_np
        self.position=(x, y, z)
        self.spawned=True

        # Create the critter instance and append to the critter list
        Entity.add_entity(self)
        
        return self
    
    