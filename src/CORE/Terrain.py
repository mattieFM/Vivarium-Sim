"""
This module provides a `TerrainController` class for managing terrain in a 3D simulation 
using Panda3D and Bullet physics. The class enables real-time terrain editing, heightfield 
collider creation, and dynamic interaction with entities affected by terrain changes.

Key Features:
- Integration with Panda3D's `GeoMipTerrain` for heightfield terrain rendering.
- Real-time terrain editing through mouse inputs, including raising and lowering terrain points.
- Dynamic heightfield collider updates for compatibility with Bullet physics.
- Automatic adjustments of entities on terrain changes.
- Scheduled tasks for continuous terrain updates and handling terrain modifications.

Dependencies:
- Panda3D: Used for rendering, handling heightmaps, and texture mapping.
- Bullet Physics: Provides collision detection and physics simulation.
- NumPy: Facilitates numerical computations and vector operations.
- Math: Used for distance and geometric calculations.
- `CORE.entity`: Manages entities interacting with the terrain.

Classes:
- TerrainController: Handles all terrain-related management, including rendering, editing, and physics integration.

Example Usage:
    from panda3d.core import ShowBase
    from terrain_module import TerrainController

    base = ShowBase()
    terrain_controller = TerrainController(base)
    base.run()
"""


from panda3d.core import KeyboardButton, GeoMipTerrain, PNMImage, TextureStage, Vec3
from direct.showbase.DirectObject import DirectObject
from panda3d.bullet import BulletRigidBodyNode, BulletHeightfieldShape, ZUp
from direct.task import Task
import numpy as np
import math

from CORE.entity import Entity

class TerrainController(DirectObject):
    """the panda Object that handles all terrain management"""
    def __init__(self,base):
        self.base = base
        self.render = base.render
        super().__init__()
        
        self.init_terrain()
        
        self.base.task_mgr.add(self.terrain_update_task, "update")
        self.base.task_mgr.add(self.handle_terrain_edit, "handleEnvironmentChange")
    
    def init_terrain(self):
        """set up our heightmap terrain stuff"""
        #--terrain setup--
        self.terrain = GeoMipTerrain("worldTerrain")
        #create the img height map
        self.heightmap = PNMImage(1025,1025,1)
        #self.heightmap.read("test.png")
        self.heightmap.write("terrain.png")
        self.terrain.set_heightfield("./terrain.png")
        #self.terrain.set_color_map("./test.png")
        
        self.grass_terrain_texture = self.base.loader.loadTexture("assets/textures/Grass001_1K-PNG_Color.png")

        self.terrain.set_block_size(128)
        self.terrain.set_near(40)
        self.terrain.set_min_level(0)
        #self.terrain.set_bruteforce(True)
        self.terrain.set_far(100)
        self.terrain.set_focal_point(self.base.camera)
        
        #store root for convenience
        self.terrain_np = self.terrain.getRoot()
        self.terrain_np.setTexture(TextureStage.getDefault(), self.grass_terrain_texture)
        self.terrain_np.setTexScale(TextureStage.getDefault(), 1)
        self.terrain_np.reparent_to(self.render)
        self.terrain_np.setSz(self.base.z_scale)
        
        #create the actual terrain
        self.terrain.generate()
    
    def create_heightFieldMap_Collider(self):
        """create/update our terrain collider"""
        #not the best solution but im not editing their engine code
        #BulletHeightfieldShape does not refresh the collision mesh when the hieght map img updates
        #so we just kill and rebuild it any time we edit
        #TODO: make this only update when a user stops holding mouse, right now it just edits after reach brush gradient finishes.
        if(hasattr(self,"ground")):
            self.base.world.remove(self.ground)
            
        #create container for our thingo
        self.ground = BulletRigidBodyNode('Ground')
        
        #the thingo in question --collider mapped to our height map
        self.shape = BulletHeightfieldShape(self.heightmap, self.base.z_scale, ZUp)
        
        #draw
        self.ground.addShape(self.shape)
        self.np = self.render.attachNewNode(self.ground)
        pos = self.get_terrain_center()
        #TODO: WHY IS THIS NUMBER NEEDED. IDK. but it yeah... it works with this here. >:3
        pos[2]=265
        
        #set to our new cool pos.
        self.np.setPos(pos)
        self.base.world.attachRigidBody(self.ground)
        
        for critter in Entity.get_entities():
            node = critter.node
            #when a node settles IE stops moving --comes to rest, it stops being thunk about by the engine
            #so we give it a bit of upward force to ensure that the thinker starts thunking again about 
            #our critter
            node.setLinearVelocity(Vec3(0, 0, .005))
            
            #this line might be enough to get it working. but the combo of them seems better? idk should be harmless to have both
            node.active=True
            
            #alternatively just move it up a little bit, but idk it wasnt working. this is a bit odd cus things fall slow if you are editing
            #but w/e its okay for now, worst case just increese gravity to fix this.
            
            node.setAngularVelocity(Vec3(0, 0, 0))
            #node.body_np.setPos(node.body_np.getPos() + Vec3(0, 0, 0.01))
    
    # Add a task to keep updating the terrain
    def terrain_update_task(self,task):
        """ensure the terrain updates to match the edits being made to the height map"""
        updating_terrain = self.terrain.update()
        if(updating_terrain): print("terrain update")
        return task.cont
    
    def get_height_at(self, x, y):
        """Get the height at a given x, y coordinate on the heightfield."""
        from main import BaseApp
        return self.terrain.get_elevation(int(x),int(y)) * BaseApp.z_scale
    
    def ascend_objs_with_terrain(self, point, radius=None, objects=[]):
        """when a terrain point is elevated, check all critters within radius and ascend them with the terrain if applicable"

        Args:
            point (_type_): _description_
        """
        
        if(radius==None): radius = self.base.edit_radius*2
        
        for critter in objects:
            body_np = critter.body_np or critter
            body_pos=body_np.get_pos()
            point[2] = body_pos[2]
            if(np.linalg.norm(body_pos-point)<radius):
                self.base.set_critter_height(body_np,body_pos[0],body_pos[1])
    
    def edit_terrain(self, modifier):
        """the function that handles modifying the terrain, when called finds the mouse and raycasts to the terrain
        then finds the pixel and real world coord of the collision. for sake of sanity I have mapped it such that 1 pixel of the height map
        is one world unit so these should mostly line up"""
        
        #define our success function
        def on_click_success(point):
            self.raise_point(point,power=modifier)
            self.create_heightFieldMap_Collider()
            print(Entity.get_entities())
            self.ascend_objs_with_terrain(point,objects=Entity.get_entities())
            
        #cast our ray
        self.base.click_on_map_and_call(on_click_success)
    
    def raise_point(self, point, max_range=None,power=.1):
        """the method that handles editing the 2d png height map

        Args:
            point (x,y): tuple, ints. the pixel to edit
            max_range (int, optional): how many pixels away to effect. Defaults to None.
            power (float, optional): how powerful the effect is, min -1 max 1. Defaults to .1.
        """
        if(max_range == None): max_range = self.base.edit_radius
        # Convert the world point to heightmap coordinates
        print(f"pointx:{point.x}, pointy:{point.y}")
        center_x = point.x #int(point.x / self.terrain_np.getScale().x * self.heightmap.getXSize())
        center_y = np.abs(point.y - self.heightmap.getYSize())#int(point.y / self.terrain_np.getScale().y * self.heightmap.getYSize())
        
        for x in range(int(center_x-max_range),int(center_x+max_range)):
            for y in range(int(center_y-max_range),int(center_y+max_range)):
                if(x>0 and y>0 and x<self.heightmap.getXSize() and y<self.heightmap.getYSize()):
                    #TODO: fix this fall off, it works in reverse currently...
                    # Calculate the distance from the center pixel
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    
                    # Normalize the distance so it's between 0 and 1
                    max_distance = math.sqrt((0 - center_x)**2 + (0 - center_y)**2)  # Max distance to any corner
                    normalized_distance = distance / max_distance
                    current_height = self.heightmap.getGray(x, y)
                    new_height = min(1.0, current_height + .1*power)  # Increase height, max 1.0
                    self.heightmap.setGray(x, y, new_height)
        
        # Update the terrain
        self.terrain.setHeightfield(self.heightmap)
        #self.terrain.generate()
        self.heightmap.write("terrain.png")
        
    def handle_terrain_edit(self, task, modifier=None):
        """the task that handles actually calling the terrain editor method. called every frame
        if edit is enabled and mouse is held then do the thing

        Args:
            task (PandaTask): the task
            modifier (float, optional): float to be how big the edit is max 1 min -1, but it wont break with bigger or smaller vals, it just will floor them. Defaults to self.edit_power.

        Returns:
            Task: run every tick
        """
        if(modifier == None): modifier = self.base.edit_power
        if(self.base.edit_terrain_enabled):
            if(self.base.input.mouse_held):
                self.edit_terrain(modifier)
            elif(self.base.input.mouse3_held):
                self.edit_terrain(modifier*-1)
            
        return Task.cont
        
    def get_terrain_center(self):
        """return the center point of the terrain (x,y,z) tuple"""
        #update the terrain so we have accurate pos
        return self.terrain.getRoot().getBounds().getCenter()