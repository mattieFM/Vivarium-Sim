from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.task import Task
from direct.actor.Actor import Actor
import numpy as np
from math import pi, sin, cos
import math
from util import Util

MIN_UI_X =-1.25
MAX_UI_X =1.25

MIN_UI_Y = .9
MAX_UI_Y = -.9

UI_Y_WIDTH = np.abs(MIN_UI_Y)+np.abs(MAX_UI_Y)
UI_X_WIDTH = np.abs(MIN_UI_X)+np.abs(MAX_UI_X)


class ConfigurableValue():
    """a class for values that can be configured via the UI"""
    def __init__(
        self,
        callback,
        label,
        is_toggle,
        scale = .05,
        y_spacing_between_elements=UI_Y_WIDTH/30,
        x_spacing_between_elements=UI_Y_WIDTH/100,
        start_x=0,
        start_y=0,
        placeholder=""
        ):
        self.callback = callback
        self.label=label
        self.is_toggle = is_toggle
        self.scale = scale
        self.y_spacing_between_elements = y_spacing_between_elements
        self.x_spacing_between_elements = x_spacing_between_elements
        self.elements = []
        self.placeholder=placeholder
        
        self.start_x=start_x
        self.start_y=start_y
        
    def destroy(self):
        """Destroy this element"""
        for element in self.elements:
            element.destroy()
    
    def update(self):
        "Destroy then redraw this element"
        self.destroy()
        self.create_ui_component(self.start_x,self.start_y)
        
    def unfocus(self):
        """unfocus any and all elements that could be focused"""
        for element in self.elements:
            #TODO:clean this up.
            try:
                element['focus'] = False
            except Exception:
                pass
    
    def create_ui_component(self,start_x,start_y):
        self.start_x=start_x
        self.start_y=start_y
        
        self.element = None
        x=start_x
        y=start_y
        
        self.labelElement = DirectLabel(text=self.label,scale=self.scale*1.4,pos=(MIN_UI_X+x,0,MIN_UI_Y+y-.015))
        
        label_width = self.labelElement.getWidth()  * self.labelElement['scale']
        
        label_x = MIN_UI_X+x+label_width*.5
        
        self.labelElement.setPos((label_x,0,MIN_UI_Y+y-.015))
        
        print(f"labelX{label_x},label_width:{label_width}")
        x = -MIN_UI_X + label_x + label_width*.5 + self.x_spacing_between_elements + .05
        print(x)
        
        self.elements.append(self.labelElement)
        
        if(self.is_toggle):
            #then render as just a toggle button and label
            self.element = DirectCheckButton(text = "" ,scale=self.scale,command=self.callback,pos=(MIN_UI_X+x,0,MIN_UI_Y+y))
            self.elements.append(self.element)
            pass
        else:
            #else render as a label input box and set button
            self.textBox = DirectEntry(scale=self.scale-.0125,pos=(MIN_UI_X+x-.039,0,MIN_UI_Y+y-.01),command=self.callback,initialText=str(self.placeholder))
            self.elements.append(self.textBox)
            text_box_width = self.textBox.getWidth()  * self.textBox['scale']
            
            x += text_box_width + self.x_spacing_between_elements
            
            def call_cb_with_text_from_textbox():
                """call the callback passing in text"""
                self.callback(self.textBox.get())
                self.textBox["focus"] = 0
            
            self.element = DirectButton(text = "Set", scale=self.scale+.0025,command=call_cb_with_text_from_textbox,pos=(MIN_UI_X+x,0,MIN_UI_Y+y-.011))
            self.elements.append(self.element)
            pass
        
        return self.element
        

class UI():
    VERTICAL_SPACING_BETWEEN_OPTIONS = UI_Y_WIDTH/25
    
    def __init__(self):
        self.configurable_values = []
        self.add_base_options()
        
    def add_base_options(self):
        """add the base options to this UI instance
        """
        #self.configurable_values.append(ConfigurableValue(lambda x: 0, "test", True))
        #self.configurable_values.append(ConfigurableValue(lambda x: print(x), "test", False))
        pass
        
    def add_option(self,option):
        """add a configurable value to the UI and update and render it

        Args:
            option (ConfigurableValue): the option to add
        """
        self.configurable_values.append(option)
        self.update()
        print(self.configurable_values)

    def update(self):
        """destroy all displayed config options then redraw all of them"""
        for value in self.configurable_values:
            value.destroy()
        
        self.setup()
        
    def unfocus_all(self):
        """unfocus all elements that can be unfocused"""
        for value in self.configurable_values:
            value.unfocus()
    
    def setup(self):
        """render all elements in a list
        """
        y=0
        print("setup")
        for value in self.configurable_values:
            value.create_ui_component(0,y)
            y-=self.VERTICAL_SPACING_BETWEEN_OPTIONS
    

class Input(DirectObject):
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
        self.accept('wheel_up', self.on_mouse_scroll, ['wheel_up'])
        self.accept('wheel_down', self.on_mouse_scroll, ['wheel_down'])
        
        self.accept("mouse1", self.on_mouse_click, ['mouse1'])
        self.accept("mouse1-up", self.on_mouse_click, ['mouse1-up'])
        
        self.accept("mouse3", self.on_mouse3_click, ['mouse3'])
        self.accept("mouse3-up", self.on_mouse3_click, ['mouse3-up'])
        
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
    edit_terrain_enabled = False
    
    #toggle add blobs
    add_blob_enabled = False
    
    #how fast to build terrain
    edit_power = .5
    
    #how big to edit 
    edit_radius = 50
    
    #the scale of z
    z_scale=500
    
    #little buddy offset
    critter_offset_z=12
      
    def __init__(self):
        ShowBase.__init__(self)
        
        #disable default mouse orbiting
        self.disable_mouse()
        
        #init our input handler class
        self.input = Input(self)
        
        self.ui = UI()
        self.ui.setup()
        
        def edit_terrain_toggle(val):
            self.edit_terrain_enabled=val
            
        def add_blob_toggle(val):
            self.add_blob_enabled=val
            
        def edit_speed(val):
            self.edit_power=float(val)
            self.ui.unfocus_all
            
        def edit_radius(val):
            self.edit_radius=float(val)
            self.ui.unfocus_all
            
        self.ui.add_option(ConfigurableValue(edit_terrain_toggle, "edit", True))
        
        self.ui.add_option(ConfigurableValue(edit_speed, "edit speed", False, placeholder=self.edit_power))
        
        self.ui.add_option(ConfigurableValue(edit_radius, "edit radius", False, placeholder=self.edit_radius))
        
        self.ui.add_option(ConfigurableValue(add_blob_toggle, "Add Guy", True))
        
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
        self.terrain_np.setSz(self.z_scale)
        
        #create the actual terrain
        self.terrain.generate()

        #click handler
        # Set up collision detection
        
        # Set up collision detection
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        
        
        #setup selection/picker handlers so we can click on objects and do things
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.cam.attach_new_node(self.picker_node)
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_ray = CollisionRay()
        self.picker_node.add_solid(self.picker_ray)
        self.picker.add_collider(self.picker_np, self.queue)
        
        self.taskMgr.add(self.updateTask, "update")
        
        self.task_mgr.add(self.handle_terrain_edit, "handleEnvironmentChange")
        
        #self.task_mgr.add(self.handle_add_guy, "handleAddGuy")
        
        #handles unfocusing from inputs when user clicks out of them
        self.accept("mouse1-up", self.handle_add_guy)
        
        self.task_mgr.add(self.handle_unfocus, "handle_unfocus")
        
        
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
                
    def handle_unfocus(self,task):
        if(self.input.mouse_held or self.input.mouse3_held):
            self.ui.unfocus_all()
        return Task.cont
        
    def handle_terrain_edit(self, task, modifier=None):
        if(modifier == None): modifier = self.edit_power
        if(self.edit_terrain_enabled):
            if(self.input.mouse_held):
                self.edit_terrain(modifier)
            elif(self.input.mouse3_held):
                self.edit_terrain(modifier*-1)
            
        return Task.cont
                
    def handle_add_guy(self):
        if(self.add_blob_enabled):
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
                
                self.blob = self.loader.loadModel("./assets/models/critter.obj")
                self.blob.setHpr(0,90,0)
                self.blob.set_pos(point[0],point[1],self.heightmap.get_gray(int(point[0]),int(np.abs(point[1] - self.heightmap.getYSize())))*self.z_scale+self.critter_offset_z)
                
                self.blob.set_scale(10)
                # Reparent the model to render.
                self.blob.reparentTo(self.render)
        return Task.cont
            
                
    def raise_point(self, point, max_range=None,power=.1):
        if(max_range == None): max_range = self.edit_radius
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
        self.heightmap.write("save.png")
        
    def get_terrain_center(self):
        """return the center point of the terrain (x,y,z) tuple"""
        #update the terrain so we have accurate pos
        return self.terrain.getRoot().getBounds().getCenter()
    

app = BaseApp()
app.run()