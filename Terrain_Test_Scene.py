from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.actor.Actor import Actor
import numpy as np
from math import pi, sin, cos
import math
from util import Util

class Input():
    VERTICAL_SPEED=1
    HORIZONTAL_SPEED=.8
    ZOOM_SPEED=30
    
    #how much should we scroll per click of a scroll wheel
    SCROLL_WHEEL_POWER = 3
    
    #invert the vertical axis if true
    INVERT_VERTICAL_AXIS = True
    
    UP_BUTTONS = [KeyboardButton.ascii_key('w')]
    DOWN_BUTTONS = [KeyboardButton.ascii_key('s')]
    
    LEFT_BUTTONS = [KeyboardButton.ascii_key('a')]
    RIGHT_BUTTONS = [KeyboardButton.ascii_key('d')]
    
    ZOOM_IN_BUTTONS = [KeyboardButton.ascii_key('q')]
    ZOOM_OUT_BUTTONS = [KeyboardButton.ascii_key('e')]
    
    #for converting the event based mouse scroll wheel interrupts into polling able
    stored_scroll_value = 0
    
    
    #both of these are always updated per tick
    mouse_held = False
    mouse3_held = False
    
    
    def __init__(self, base):
        """_summary_

        Args:
            base (BaseApp): the base app reference
        """
        self.base = base
        
        # Setup event listeners for the mouse wheel
        self.base.accept('wheel_up', self.on_mouse_scroll, ['wheel_up'])
        self.base.accept('wheel_down', self.on_mouse_scroll, ['wheel_down'])
        
        self.base.accept("mouse1", self.on_mouse_click, ['mouse1'])
        self.base.accept("mouse1-up", self.on_mouse_click, ['mouse1-up'])
        
        self.base.accept("mouse3", self.on_mouse3_click, ['mouse3'])
        self.base.accept("mouse3-up", self.on_mouse3_click, ['mouse3-up'])
        
    def on_mouse_click(self,event):
        print(f"event:{event}")
        if event == 'mouse1':
            self.mouse_held=True
        elif event == 'mouse1-up':
            self.mouse_held=False
            
    def on_mouse3_click(self,event):
        print(f"event:{event}")
        if event == 'mouse3':
            self.mouse3_held=True
        elif event == 'mouse3-up':
            self.mouse3_held=False
        
    def on_mouse_scroll(self, event):
        """handle mouse scroll wheel event by adding it into the stored value to be retrieved next time the axis is called

        Args:
            event (string): the scroll event
        """
        if event == 'wheel_up':
            self.stored_scroll_value+=-1*self.SCROLL_WHEEL_POWER
        elif event == 'wheel_down':
            self.stored_scroll_value+=1*self.SCROLL_WHEEL_POWER
        
    def get_axis(self,positiveKeys,negativeKeys):
        """get the value of an axis of input, checking if positivekeys or negative keys are held

        Args:
            positiveKeys (ButtonHandle[]): what keys positively impact this axis
            negativeKeys (ButtonHandle[]): what keys negatively impact this axis

        Returns:
            float: -1, 0 or 1 based on what inputs are held 
        """
        positiveKeysArePressed = self.any_key_is_pressed(positiveKeys)
        negativeKeysArePressed = self.any_key_is_pressed(negativeKeys)
        
        return positiveKeysArePressed - negativeKeysArePressed

        
    def get_horizontal_axis(self):
        """get the value of the horizontal input axis"""
        return self.get_axis(self.RIGHT_BUTTONS,self.LEFT_BUTTONS) * self.HORIZONTAL_SPEED
    
    def get_vertical_axis(self):
        """get the value of the vertical input axis"""
        return self.get_axis(self.UP_BUTTONS,self.DOWN_BUTTONS) * self.VERTICAL_SPEED * (-1 if self.INVERT_VERTICAL_AXIS else 1)
    
    def get_zoom_axis(self):
        """get the value of the zoom input axis"""
        keyboardZoom = self.get_axis(self.ZOOM_IN_BUTTONS,self.ZOOM_OUT_BUTTONS)
        stored_value = self.stored_scroll_value
        self.stored_scroll_value=0
        return keyboardZoom + stored_value * self.ZOOM_SPEED
        
    def any_key_is_pressed(self, keys):
        """check if any key in a list of KeyBoardKeys is held down

        Args:
            keys (KeyboardButton): _description_

        Returns:
            bool: weather any of the keys are held down
        """
        is_down = self.base.mouseWatcherNode.is_button_down
        return any(is_down(key) for key in keys)
    

class CameraController():
    #how far away from our orbit point should be be
    VIEW_DISTANCE = 1000
    MIN_PITCH=0
    MAX_PITCH=82
    
    def __init__(self, base, get_orbit_point,input,cam,taskMgr):
        """

        Args:
            base (BaseApp): the base app reference
            orbit_point (Vec3): the point that this controller will rotate around
        """
        self.base = base
        self.get_orbit_point = get_orbit_point
        self.input=input
        self.cam=cam
        self.taskMgr=taskMgr
    
    def set_cam_origin_to_terrain_center(self):
        """move the cam origin to the terrain center to make rotation easy"""
        self.cam_pivot_point = NodePath('cam_pivot')
        self.cam_pivot_point.reparent_to(self.base.render)
        self.cam_pivot_point.set_pos(self.get_orbit_point())
        self.cam_pivot_point.setHpr(0,0,0)
        #set the cam's rotational parent to the cam pivot point
        self.cam.wrt_reparent_to(self.cam_pivot_point)
        
    def setupCamControls(self):
        """handle the initialization of camera controller 
        """
        #move cam to start pos yay!
        self.move_cam_to_start_pos()
        
        #init the pivot point
        self.set_cam_origin_to_terrain_center()
        
        #add our controller
        self.taskMgr.add(self.move_cam_task, "CameraControl")
        
    def move_cam_task(self, task):
        horizontal = self.input.get_horizontal_axis()
        vertical = self.input.get_vertical_axis()
        zoom = self.input.get_zoom_axis()
        
        #handle rotation
        if(horizontal != 0 or vertical != 0):
            #get the initial heading pitch and yaw
            pivot_hpr = self.cam_pivot_point.getHpr()
            
            #update
            heading = pivot_hpr[0]+horizontal
            pitch = Util.clamp(pivot_hpr[1]+vertical,self.MIN_PITCH,self.MAX_PITCH)
            yaw = pivot_hpr[2]
            
            #set
            self.cam_pivot_point.setHpr(heading,pitch,yaw)
        
        #handle zoom
        
        if(zoom != 0):
            camera_pos = self.cam.get_pos()
            
            # since we are using parent for rotation we can just move the z axis closer
            camera_pos[2] += zoom
            self.cam.set_pos(camera_pos)
        
        return Task.cont
    
    def move_cam_to_start_pos(self):
        """move the cam to above the terrain looking at center"""
        pos = self.get_orbit_point()
        pos[2] = self.VIEW_DISTANCE
        self.cam.set_pos(pos)
        self.cam.look_at(self.get_orbit_point())

class BaseApp(ShowBase):     
    #so that it can be turned off if we want to
    edit_terrain_enabled = True
      
    def __init__(self):
        ShowBase.__init__(self)
        
        #disable default mouse orbiting
        self.disable_mouse()
        
        #init our input handler class
        self.input = Input(self)
        
        #--terrain setup--
        self.terrain = GeoMipTerrain("worldTerrain")
        
        # Create a directional light (like sunlight)
        self.dlight = DirectionalLight('dlight')
        self.dlight.setColor((3, 3, 3, 1))
        self.dlight.set_shadow_caster(True)
        self.dlnp = self.render.attachNewNode(self.dlight)
        self.dlnp.setHpr(0, -35, 0)
        self.dlight.getLens().setNearFar(1000,1500)
        self.dlight.getLens().setFilmSize(30, 30)
        self.render.setLight(self.dlnp)
        
        self.alight = self.render.attachNewNode(AmbientLight("Ambient"))
        self.alight.node().setColor(LVector4(.6, .6, .6, 1))
        self.render.setLight(self.alight)
        
        self.render.setShaderAuto()
        
        # Load and compile the shader
        #self.shader = Shader.load(Shader.SL_GLSL, "./assets/shaders/shadow_shader.vert", "./assets/shaders/shadow_shader.frag")
        
        #create the img height map
        self.heightmap = PNMImage(1025,1025,1)
        #self.heightmap.read("test.png")
        self.heightmap.write("test.png")
        self.terrain.set_heightfield("./test.png")
        #self.terrain.set_color_map("./test.png")
        
        self.grass_terrain_texture = self.loader.loadTexture("assets/textures/Grass001_1K-PNG_Color.png")

        self.terrain.set_block_size(128)
        self.terrain.set_near(40)
        self.terrain.set_min_level(0)
        #self.terrain.set_bruteforce(True)
        self.terrain.set_far(100)
        self.terrain.set_focal_point(self.camera)
        
        #store root for convenience
        self.terrain_np = self.terrain.getRoot()
        self.terrain_np.setTexture(TextureStage.getDefault(), self.grass_terrain_texture)
        self.terrain_np.setTexScale(TextureStage.getDefault(), 1)
        self.terrain_np.reparent_to(self.render)
        self.terrain_np.setSz(500)
        
        #create the actual terrain
        self.terrain.generate()

        #click handler
        # Set up collision detection
        
        # Set up collision detection
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.3, 0.3, 0.3)
        self.pandaActor.reparentTo(self.render)
        
        
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.cam.attach_new_node(self.picker_node)
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_ray = CollisionRay()
        self.picker_node.add_solid(self.picker_ray)
        self.picker.add_collider(self.picker_np, self.queue)
        
        self.taskMgr.add(self.updateTask, "update")
        self.task_mgr.add(self.handle_terrain_edit, "handleEnvironmentChange")
        
        #init our camera controller
        self.camera_controller = CameraController(
            self,
            self.get_terrain_center,
            self.input,
            self.cam,
            self.task_mgr
            )
        
        #turn on camera control
        self.camera_controller.setupCamControls()
        
        #self.accept("mouse1", self.on_click)
        
    # Add a task to keep updating the terrain
    def updateTask(self,task):
        updating_terrain = self.terrain.update()
        if(updating_terrain): print("terrain update")
        return task.cont
    
    def edit_terrain(self, modifier):
        if self.mouseWatcherNode.hasMouse():
            # Get mouse position
            mpos = self.mouseWatcherNode.getMouse()
            print(f"mpos:{mpos}")
            
            # Update ray position
            
            self.picker_ray.setFromLens(self.cam.node(), mpos.x, mpos.y)
            print("here2")
            self.picker.traverse(self.render)
            if self.queue.getNumEntries() > 0:
                print("collide")
                # Get the first collision
                self.queue.sortEntries()
                entry = self.queue.getEntry(0)
                
                # Find the collision point
                point = entry.getSurfacePoint(self.terrain_np)
                self.raise_point(point,power=modifier)
        
    def handle_terrain_edit(self, task, modifier=.5):
        if(self.edit_terrain_enabled):
            if(self.input.mouse_held):
                self.edit_terrain(modifier)
            elif(self.input.mouse3_held):
                self.edit_terrain(modifier*-1)
            
        return Task.cont
                
    def raise_point(self, point, max_range=50,power=.1):
        # Convert the world point to heightmap coordinates
        print(f"pointx:{point.x}, pointy:{point.y}")
        center_x = point.x #int(point.x / self.terrain_np.getScale().x * self.heightmap.getXSize())
        center_y = np.abs(point.y - self.heightmap.getYSize())#int(point.y / self.terrain_np.getScale().y * self.heightmap.getYSize())
        
        for x in range(int(center_x-max_range),int(center_x+max_range)):
            for y in range(int(center_y-max_range),int(center_y+max_range)):
                if(x>0 and y>0 and x<self.heightmap.getXSize() and y<self.heightmap.getYSize()):
                    #TODO: fix this fall off, it works in reverse currently.
                    # Calculate the distance from the center pixel
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    
                    # Normalize the distance so it's between 0 and 1
                    max_distance = math.sqrt((0 - center_x)**2 + (0 - center_y)**2)  # Max distance to any corner
                    normalized_distance = distance / max_distance
                    current_height = self.heightmap.getGray(x, y)
                    new_height = min(1.0, current_height + normalized_distance*power)  # Increase height, max 1.0
                    self.heightmap.setGray(x, y, new_height)
                
        

                    
        # Update the terrain
        self.terrain.setHeightfield(self.heightmap)
        #self.terrain.generate()
        self.heightmap.write("save.png")
        
    def get_terrain_center(self):
        """return the center point of the terrain (x,y,z) tuple"""
        #update the terrain so we have accurate pos
        return self.terrain.getRoot().getBounds().getCenter()
    

app = BaseApp()
app.run()