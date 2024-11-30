import random
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.bullet import BulletHeightfieldShape, BulletDebugNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import ZUp
from panda3d.bullet import BulletWorld
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.physics import *
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


class RoundManager:
    """Manages the lifecycle phases of a simulation round."""

    PHASES = ["Initialization", "Simulation", "Evaluation", "Reproduction"]

    def __init__(self, base_app, population_cap=100):
        """
        Initialize the round manager.

        Args:
            base_app (BaseApp): Reference to the main app.
            population_cap (int): Maximum number of critters allowed.
        """
        self.base_app = base_app
        self.current_phase_index = 0
        self.population_cap = population_cap

    def get_current_phase(self):
        """Return the current phase name."""
        return self.PHASES[self.current_phase_index]

    def next_phase(self):
        """Advance to the next phase in the cycle."""
        self.current_phase_index = (self.current_phase_index + 1) % len(self.PHASES)
        self.trigger_phase_start()

    def trigger_phase_start(self):
        """Trigger the start of the current phase."""
        phase = self.get_current_phase()
        print(f"Starting Phase: {phase}")
        if phase == "Initialization":
            self.base_app.initialize_round()
        elif phase == "Simulation":
            self.base_app.simulate_round()
        elif phase == "Evaluation":
            self.base_app.evaluate_round()
        elif phase == "Reproduction":
            self.base_app.reproduce_round()


class Gene:
    """Class representing a single gene in a critter's genetic makeup."""

    def __init__(self, name, value, min_value=None, max_value=None, mutation_rate=0.1, mutation_step=0.1,
                 options=None, dominance=1, generation=0, parent_ids=None):
        """
        Initialize a new gene with its properties.
        
        Args:
            name (str): The name of the gene (something like "Strength").
            value (int, float, or str): The initial value of the gene.
            min_value (int or float, optional): Minimum value for the gene (if numeric).
            max_value (int or float, optional): Maximum value for the gene (if numeric).
            mutation_rate (float): Probability of mutation (0 to 1).
            mutation_step (float): Step size for numeric mutations.
            options (list, optional): Allowed values for categorical genes (if applicable).
            dominance (int, optional): Priority for crossover (higher value dominates).
            generation (int, optional): Generation in which this gene was created.
            parent_ids (list, optional): List of parent gene names for lineage tracking.
        """
        self.name = name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.mutation_rate = mutation_rate
        self.mutation_step = mutation_step
        self.options = options or []  # For categorical genes
        self.dominance = dominance
        self.generation = generation
        self.parent_ids = parent_ids or []
        self.active = True  # By default, the gene is active

    def mutate(self):
        """
        Mutate the gene's value based on its mutation rate and step size.
        
        Numeric genes are incremented/decremented within their bounds.
        Categorical genes are randomly changed within their options.
        """
        if not self.active:
            return  # Skip mutation if the gene is inactive

        if random.random() < self.mutation_rate:  # Check if mutation occurs
            if isinstance(self.value, (int, float)):  # Numeric mutation
                mutation = random.uniform(-self.mutation_step, self.mutation_step)
                new_value = self.value + mutation
                if self.min_value is not None and self.max_value is not None:
                    self.value = max(self.min_value, min(new_value, self.max_value))
                else:
                    self.value = new_value
            elif isinstance(self.value, str) and self.options:  # Categorical mutation
                self.value = random.choice(self.options)

    def crossover(self, other):
        """
        Perform crossover with another gene to create an offspring gene.
        
        Args:
            other (Gene): The other parent gene.
        
        Returns:
            Gene: A new gene combining properties from both parents.
        """
        if not isinstance(other, Gene):
            raise ValueError("Crossover requires another Gene instance.")
        
        # Value inheritance based on dominance
        new_value = self.value if self.dominance >= other.dominance else other.value
        
        return Gene(
            name=self.name,
            value=new_value,
            min_value=self.min_value,
            max_value=self.max_value,
            mutation_rate=(self.mutation_rate + other.mutation_rate) / 2,
            mutation_step=(self.mutation_step + other.mutation_step) / 2,
            dominance=max(self.dominance, other.dominance),
            generation=max(self.generation, other.generation) + 1,
            parent_ids=[self.name, other.name]
        )

    def decay(self, rate=0.01):
        """
        Simulate gene decay by gradually decreasing its value.
        
        Args:
            rate (float): The rate of decay (default is 0.01).
        """
        if isinstance(self.value, (int, float)):
            self.value = max(self.min_value, self.value - rate)

    def __str__(self):
        """Return a string of the gene."""
        return (f"Gene(Name={self.name}, Value={self.value}, Min={self.min_value}, Max={self.max_value}, "
                f"MutationRate={self.mutation_rate}, MutationStep={self.mutation_step}, "
                f"Dominance={self.dominance}, Generation={self.generation})")


class Critter:
    """Class representing a critter in the simulation."""

    _id_counter = 0  # Class-level counter to assign unique IDs to each critter

    def __init__(self, position=(0, 0, 0), strength=1.0, color=(1, 1, 1, 1), genes=None, node=None):
        """
        Initialize a new critter.
        
        Args:
            position (tuple): Initial (x, y, z) position of the critter.
            strength (float): Ability to climb steep terrain.
            color (tuple): RGBA color representing the critter visually.
            genes (list or dict): List of Gene objects representing the critter's genetic makeup.
        """
        self.id = Critter._id_counter  # Assign a unique ID
        Critter._id_counter += 1  # Increment ID counter
        self.position = position
        self.strength = strength
        self.color = color
        self.genes = genes if genes is not None else [
            Gene("Strength", strength, min_value=0.5, max_value=2.0)
        ]  # Default to a strength gene
        self.fitness = 0  # Initialize fitness score
        self.node = node

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
    #since a click is required to toggle on the blob mode this stops a critter from spawning when blob is toggled on via the button
    add_first_blob_enabled = False
    
    #how fast to build terrain
    edit_power = .5
    
    #how big to edit 
    edit_radius = 50
    
    #the scale of z
    z_scale=500
    
    blobi=0
    
    tmpBlobs = []
    
    #little buddy offset
    critter_offset_z=12
    
    CRITTER_COLORS = [
    (1, 0, 0, 1),  # Red
    (0, 1, 0, 1),  # Green
    (0, 0, 1, 1),  # Blue
    (1, 1, 0, 1),  # Yellow
    ]
      
    def __init__(self):
        ShowBase.__init__(self)
        
        #disable default mouse orbiting. it is bad we want our own system.
        self.disable_mouse()
        
        #init our input handler class
        self.input = Input(self)
        
        #init our UI
        self.create_UI()
        
        #create our lights
        self.create_lights()
        
        # Create our skybox
        self.add_skybox()
        
        #setup our terrain
        self.init_terrain()

        #set up colliders and picker
        self.picker_setup()
        
        #set up bullet grav and phys engine
        self.init_gravity()
        
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
        
        #--Event Handlers--
        self.event_handlers_setup()
        
        # List to keep track of food in the world  
        self.max_food_count = 20  # The maximum number of food items allowed in the world     
        self.food_items = []
        
        # Spawn initial foods - 5 for now, can adjust to modify balancing
        for _ in range(5):
            self.spawn_food()
            
        # Start the periodic food spawning task
        self.taskMgr.doMethodLater(
            random.uniform(3, 5),  # Initial delay
            self.spawn_food_periodically,
            "FoodSpawnTask"
        )
        
        # List to track all critters
        self.critters = []
        
        
        self.round_manager = RoundManager(self)
        
        # task to advance phases every 20 seconds
        self.taskMgr.doMethodLater(20, self.advance_round_phase, "AdvancePhaseTask")

        
    def event_handlers_setup(self):
        """set up all event handlers for the app"""
        #handles updating the terrain, that is when the Image is edited update the mesh
        self.taskMgr.add(self.terrain_update_task, "update")
        
        #this makes sure when we stop looking at the ui it becomes unfocused
        self.task_mgr.add(self.handle_unfocus, "handle_unfocus")
        
        #handles all terrain editing 
        self.task_mgr.add(self.handle_terrain_edit, "handleEnvironmentChange")
        
        #handles un-focusing from inputs when user clicks out of them
        self.accept("mouse1-up", self.handle_add_guy)
        
        # Press 'f' to manually spawn food
        self.accept('f', self.spawn_food)
        
        # Press 'r' to reset all food in the world
        self.accept('r', self.reset_all_food)
        
            
        # Print critters with 'p'
        self.accept('p', lambda: [print(critter) for critter in self.critters])
        
        # Press spacebar to start the round manager
        self.accept('space', self.start_round_manager)

    def picker_setup(self):
        """set up everything we need for collisions and our picker.
        this is used for the raytracing to draw on our map and to pick objects
        this can also allow us to select individual critters and such if we ever
        want to target them
        """
        # Set up collision detection and click handler
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        self.pusher = CollisionHandlerPusher()
        
        #setup selection/picker handlers so we can click on objects and do things
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.cam.attach_new_node(self.picker_node)
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_ray = CollisionRay()
        self.picker_node.add_solid(self.picker_ray)
        self.picker.add_collider(self.picker_np, self.queue)
        
    def create_UI(self):
        """Initialize the UI."""
        self.ui = UI()
        self.ui.setup()

        def edit_terrain_toggle(val):
            self.edit_terrain_enabled = val

        def add_blob_toggle(val):
            self.add_blob_enabled = val
            self.add_first_blob_enabled = val

        def edit_speed(val):
            self.edit_power = float(val)
            self.ui.unfocus_all()

        def edit_radius(val):
            self.edit_radius = float(val)
            self.ui.unfocus_all()

        self.ui.add_option(ConfigurableValue(edit_terrain_toggle, "edit", True))
        self.ui.add_option(ConfigurableValue(add_blob_toggle, "Add Critter", True))
        self.ui.add_option(ConfigurableValue(edit_speed, "edit speed", False, placeholder=self.edit_power))
        self.ui.add_option(ConfigurableValue(edit_radius, "edit radius", False, placeholder=self.edit_radius))

        # Return the UI
        return self.ui

        
        
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
    
    def create_lights(self):
        """lights... idk what to tell you they are lights"""
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
        
    def init_gravity(self):
        """set up our bullet phys and grav
        """
        #create world
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        
        #set to update every frame. delta time is handled inside the update.
        self.taskMgr.add(self.update_grav, "Update_Grav")
        
        #call once to ensure that collision works without editing     
        #IE: create our terrain collision mesh once here   
        self.create_heightFieldMap_Collider()
        
    def bullet_debugger_ON(self):
        """rip all frames if this is on... but it does show the colliders. but 1 fps. idc enough to figure out how to make it a toggle so this just turns it on."""
        # Set up debug rendering
        #this works for debug rendering but will be slow as hell
        debug_node = BulletDebugNode("Debug")
        debug_node.showWireframe(True)
        debug_node.showConstraints(True)
        debug_node.showBoundingBoxes(False)
        debug_np = self.render.attachNewNode(debug_node)
        debug_np.show()  # Make sure it's visible
        self.world.setDebugNode(debug_node)
        
        
    def create_heightFieldMap_Collider(self):
        """create/update our terrain collider"""
        #not the best solution but im not editing their engine code
        #BulletHeightfieldShape does not refresh the collision mesh when the hieght map img updates
        #so we just kill and rebuild it any time we edit
        #TODO: make this only update when a user stops holding mouse, right now it just edits after reach brush gradient finishes.
        if(hasattr(self,"ground")):
            self.world.remove(self.ground)
            
        #create container for our thingo
        self.ground = BulletRigidBodyNode('Ground')
        
        #the thingo in question --collider mapped to our height map
        self.shape = BulletHeightfieldShape(self.heightmap, self.z_scale, ZUp)
        
        #draw
        self.ground.addShape(self.shape)
        self.np = self.render.attachNewNode(self.ground)
        pos = self.get_terrain_center()
        #TODO: WHY IS THIS NUMBER NEEDED. IDK. but it yeah... it works with this here. >:3
        pos[2]=265
        
        #set to our new cool pos.
        self.np.setPos(pos)
        self.world.attachRigidBody(self.ground)
        
        for node,np in self.tmpBlobs:
            #when a node settles IE stops moving --comes to rest, it stops being thunk about by the engine
            #so we give it a bit of upward force to ensure that the thinker starts thunking again about 
            #our critter
            node.setLinearVelocity(Vec3(0, 0, .005))
            
            #this line might be enough to get it working. but the combo of them seems better? idk should be harmless to have both
            node.active=True
            
            #alternatively just move it up a little bit, but idk it wasnt working. this is a bit odd cus things fall slow if you are editing
            #but w/e its okay for now, worst case just increese gravity to fix this.
            
            #node.setAngularVelocity(Vec3(0, 0, 1))
            #node.body_np.setPos(node.body_np.getPos() + Vec3(0, 0, 0.01))
        
        
    
    def update_grav(self,task):
        """update the gravity phys of the world, use delta time to account for fps differences"""
        dt = globalClock.getDt()
        self.world.doPhysics(dt)
        #self.create_heightFieldMap_Collider()
        return task.cont
                
    # Add a task to keep updating the terrain
    def terrain_update_task(self,task):
        """ensure the terrain updates to match the edits being made to the height map"""
        updating_terrain = self.terrain.update()
        if(updating_terrain): print("terrain update")
        return task.cont
    
    def click_on_map_and_call(self,callback):
        """cast a ray from the user's camera to their cursor, if the ray
        hits the terrain then we calculate the pos of that collision and pass the point of collision (x,y,z) Vec3
        into the callback

        Args:
            callback (function(Vec3)): the callback to call if we find the intersection point
        """
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
                callback(point)
                
    def ascend_critter_with_terrain(self,point, radius=None):
        """when a terrain point is elevated, check all critters within radius and ascend them with the terrain if applicable"

        Args:
            point (_type_): _description_
        """
        
        if(radius==None): radius = self.edit_radius*2
        
        for node,body_np in self.tmpBlobs:
            print(node)
            print(body_np)
            body_pos=body_np.get_pos()
            if(np.linalg.norm(body_pos-point)<radius):
                self.set_critter_height(body_np,body_pos[0],body_pos[1])
                
        
    def edit_terrain(self, modifier):
        """the function that handles modifying the terrain, when called finds the mouse and raycasts to the terrain
        then finds the pixel and real world coord of the collision. for sake of sanity I have mapped it such that 1 pixel of the height map
        is one world unit so these should mostly line up"""
        
        #define our success function
        def on_click_success(point):
            self.raise_point(point,power=modifier)
            self.create_heightFieldMap_Collider()
            self.ascend_critter_with_terrain(point)
            
        #cast our ray
        self.click_on_map_and_call(on_click_success)
                
                
    def handle_unfocus(self,task):
        """a simple task called every frame, if either mouse button clicks outside of the UI unfocus all UI elements"""
        if(self.input.mouse_held or self.input.mouse3_held):
            self.ui.unfocus_all()
        return Task.cont
        
    def handle_terrain_edit(self, task, modifier=None):
        """the task that handles actually calling the terrain editor method. called every frame
        if edit is enabled and mouse is held then do the thing

        Args:
            task (PandaTask): the task
            modifier (float, optional): float to be how big the edit is max 1 min -1, but it wont break with bigger or smaller vals, it just will floor them. Defaults to self.edit_power.

        Returns:
            Task: run every tick
        """
        if(modifier == None): modifier = self.edit_power
        if(self.edit_terrain_enabled):
            if(self.input.mouse_held):
                self.edit_terrain(modifier)
            elif(self.input.mouse3_held):
                self.edit_terrain(modifier*-1)
            
        return Task.cont
    
    
    def summon_critter(self, x, y, color=None):
        """a method to bring forth a phys enabled critter at chosen pos, height is automatic based on height map

        Args:
            x (float): _description_
            y (float): _description_
            color (tuple, optional): The color of the critter. Randomized if not provided.
        """
        # Load the visual model for the critter
        blob = self.loader.loadModel("./assets/models/critter.obj")
        blob.setHpr(0, 90, 0)
        shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))

        # Create a BulletRigidBodyNode for physics
        node = BulletRigidBodyNode(f'Box-{self.blobi}')

        # Increment blobie (unique identifier for each physics node)
        self.blobi += 1

        # uhhh mass?
        node.setMass(1.0)
        node.addShape(shape)

        # Create phys ctrl ish, intermediate connected to real phys controller
        blob_np = self.render.attachNewNode(node)

        # lights??!?! idk
        blob.flattenLight()

        # Set parent to phys ctrl
        blob.reparentTo(blob_np)

        # Attach to the Bullet physics world
        self.world.attachRigidBody(node)

        # Adjust the critter's height based on the terrain
        self.set_critter_height(blob_np, x, y)
        blob_np.get_pos

        # Append to temporary blob tracking
        self.tmpBlobs.append((node, blob_np))
        blob.set_scale(10)

        # Assign a random color if none is provided
        if color is None:
            color = random.choice(self.CRITTER_COLORS)
        blob.setColor(*color)

        # Create the critter instance and append to the critter list
        critter = Critter(position=(x, y, 0), strength=random.uniform(0.5, 2.0), color=color, node=blob_np)
        self.critters.append(critter)

        print(f"Spawned {critter}")

        
        
    def set_critter_height(self,blob_np,x,y):
        blob_np.set_pos(x,y,self.heightmap.get_gray(int(x),int(np.abs(y - self.heightmap.getYSize())))*self.z_scale+self.critter_offset_z+10)
                
    def handle_add_guy(self):
        """a method that handles adding a little buddy wherever the user clicks
        called every frame, if add blob is enabled and the user left clicks we will spawn a physics enabled buddy at their cursor location

        Returns:
            Task: run every frame
        """
        if(self.add_blob_enabled and not self.edit_terrain_enabled):
            if(not self.add_first_blob_enabled):
                #define our success function
                def on_click_success(point):
                    #ceaseless watcher turn your gaze upon this critter :p
                    self.summon_critter(int(point[0]),int(point[1]))
                    
                #cast our ray
                self.click_on_map_and_call(on_click_success)
            else:
                self.add_first_blob_enabled=False
        
        return Task.cont
            
                
    def raise_point(self, point, max_range=None,power=.1):
        """the method that handles editing the 2d png height map

        Args:
            point (x,y): tuple, ints. the pixel to edit
            max_range (int, optional): how many pixels away to effect. Defaults to None.
            power (float, optional): how powerful the effect is, min -1 max 1. Defaults to .1.
        """
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
        self.heightmap.write("terrain.png")
        
    def get_terrain_center(self):
        """return the center point of the terrain (x,y,z) tuple"""
        #update the terrain so we have accurate pos
        return self.terrain.getRoot().getBounds().getCenter()
    
    
    def create_cube(self):
        """Programmatically create a cube geometry for the skybox with inward-facing normals and UV mapping."""
        format = GeomVertexFormat.getV3n3t2()  # Include vertex, normal, and UV data
        vdata = GeomVertexData('cube', format, Geom.UHStatic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        uv = GeomVertexWriter(vdata, 'texcoord')

        # Vertices, UVs, and normals for each face
        vertices = [
            # Front face (inward)
            (-1, -1, -1), (0, 0), (0, 0, -1),
            (1, -1, -1), (1, 0), (0, 0, -1),
            (1, 1, -1), (1, 1), (0, 0, -1),
            (-1, 1, -1), (0, 1), (0, 0, -1),

            # Back face (inward)
            (1, -1, 1), (0, 0), (0, 0, 1),
            (-1, -1, 1), (1, 0), (0, 0, 1),
            (-1, 1, 1), (1, 1), (0, 0, 1),
            (1, 1, 1), (0, 1), (0, 0, 1),

            # Left face (inward)
            (-1, -1, 1), (0, 0), (-1, 0, 0),
            (-1, -1, -1), (1, 0), (-1, 0, 0),
            (-1, 1, -1), (1, 1), (-1, 0, 0),
            (-1, 1, 1), (0, 1), (-1, 0, 0),

            # Right face (inward)
            (1, -1, -1), (0, 0), (1, 0, 0),
            (1, -1, 1), (1, 0), (1, 0, 0),
            (1, 1, 1), (1, 1), (1, 0, 0),
            (1, 1, -1), (0, 1), (1, 0, 0),

            # Top face (inward)
            (-1, 1, -1), (0, 1), (0, 1, 0),
            (1, 1, -1), (1, 1), (0, 1, 0),
            (1, 1, 1), (1, 0), (0, 1, 0),
            (-1, 1, 1), (0, 0), (0, 1, 0),

            # Bottom face (inward)
            (-1, -1, -1), (0, 0), (0, -1, 0),
            (1, -1, -1), (1, 0), (0, -1, 0),
            (1, -1, 1), (1, 1), (0, -1, 0),
            (-1, -1, 1), (0, 1), (0, -1, 0)
        ]

        # Write vertices, UVs, and normals
        for i in range(0, len(vertices), 3):
            vert, tex, norm = vertices[i], vertices[i + 1], vertices[i + 2]
            vertex.addData3(*vert)
            uv.addData2(*tex)
            normal.addData3(*norm)

        # The 12 triangles of a cube
        indices = [
            # Front face
            0, 1, 2, 2, 3, 0,
            # Back face
            4, 5, 6, 6, 7, 4,
            # Left face
            8, 9, 10, 10, 11, 8,
            # Right face
            12, 13, 14, 14, 15, 12,
            # Top face
            16, 17, 18, 18, 19, 16,
            # Bottom face
            20, 21, 22, 22, 23, 20
        ]

        tris = GeomTriangles(Geom.UHStatic)
        for i in range(0, len(indices), 3):
            tris.addVertices(indices[i], indices[i + 1], indices[i + 2])

        cube = Geom(vdata)
        cube.addPrimitive(tris)

        node = GeomNode('cube')
        node.addGeom(cube)
        
        return NodePath(node)


    def add_skybox(self):
        """Create and add a textured skybox."""
        # Create the cube programmatically (instead of downloading one online)
        self.skybox = self.create_cube()

        # Scale and center the cube
        self.skybox.setScale(10000)
        self.skybox.setPos(0, 0, 0)

        # Apply textures to each face
        faces = [
            'assets/textures/bluecloud_ft.jpg',  # Front
            'assets/textures/bluecloud_bk.jpg',  # Back
            'assets/textures/bluecloud_up.jpg',  # Top
            'assets/textures/bluecloud_dn.jpg',  # Bottom
            'assets/textures/bluecloud_lf.jpg',  # Left
            'assets/textures/bluecloud_rt.jpg',  # Right
        ]

        # Load and apply textures to the cube directly
        for i, face in enumerate(faces):
            tex = self.loader.loadTexture(face)
            if tex is None:
                print(f"Error: Could not load texture {face}")
            else:
                # Assign the texture to the appropriate face
                self.skybox.setTexture(tex, i)

        # Disable backface culling and make sure the skybox is unaffected by lighting
        self.skybox.setTwoSided(True)
        self.skybox.setLightOff()
        self.skybox.setBin('background', 0)
        self.skybox.setDepthWrite(False)

        # Reparent the skybox to render
        self.skybox.reparentTo(self.render)


    def spawn_food(self, x=None, y=None):
        """Spawn a food item at a random position on the terrain. Including elevated terrain."""
        
        # Check if we have reached the food limit
        if len(self.food_items) >= self.max_food_count:
            return  # Prevent spawning more food
        
        # Choose random x and y within the terrain bounds
        if x is None or y is None:
            x = random.uniform(0, self.heightmap.getXSize())
            y = random.uniform(0, self.heightmap.getYSize())
        
        # Convert heightmap coordinates to world coordinates
        z = self.heightmap.getGray(
            int(x), int(self.heightmap.getYSize() - y)
        ) * self.z_scale  # Terrain height at (x, y)
    
        # Load the food model - just used the cube that was already there for now
        food = self.loader.loadModel("assets/models/cube.stl")
        food.setScale(4)  # Scale the food
        food.setColor(1, 0, 0, 1)
                
        # Position the food in the world
        food.setPos(x, y, z + 5)  # Slight offset above the terrain to avoid clipping
    
        # Reparent the food to render so it appears in the scene
        food.reparentTo(self.render)
    
        # Add the food to the tracking list
        self.food_items.append(food)


    def spawn_food_periodically(self, task):
        """Spawn a food item at random intervals and reschedule dynamically."""
        self.spawn_food()

        # Schedule the next spawn between 3-5 seconds - Can adjust the timings based on how the GA works.
        next_spawn_time = random.uniform(3, 5)
        self.taskMgr.doMethodLater(
            next_spawn_time,
            self.spawn_food_periodically,
            "FoodSpawnTask"
        )
        return task.done
    
    
    def reset_all_food(self):
        """Remove all food items from the scene and reset the list. Can be called on round resets or user-input."""
        for food in self.food_items:
            food.removeNode()  # Remove the food from the scene
        self.food_items.clear()  # Clear the tracking list
        print("All food has been removed.")
        
    ### Round Based Methods ###
    def initialize_round(self):
        """Handle initialization tasks, such as spawning food and resetting critters."""
        print("Setting up a new round...")

        if len(self.critters) == 0:
            # If no critters exist, spawn a default population
            print("No critters found! Spawning initial critter population...")
            self.spawn_initial_population()

        # Reset fitness scores and reposition existing critters
        for critter in self.critters:
            critter.fitness = 0  # Reset fitness scores
            if critter.node:
                self.set_critter_height(critter.node, critter.position[0], critter.position[1])  # Reset positions
        print(f"{len(self.critters)} critters reset for the new round.")
        
    def spawn_initial_population(self, count=10):
        """Spawn an initial population of critters randomly within the terrain."""
        for _ in range(count):
            # Generate random positions on the map
            x = random.uniform(0, self.heightmap.getXSize())
            y = random.uniform(0, self.heightmap.getYSize())
            self.summon_critter(x, y)
        print(f"Spawned {count} critters for the initial population.")
        
    def simulate_round(self):
        """Simulate critter movement and interactions."""
        print("Beginning simulation!")
        # TODO: Implement critter movement logic
        print("Simulation complete!")

    def is_touching(self, critter_pos, food_pos, threshold=10):
        """
        Check if a critter is touching a food item.
    
        Args:
            critter_pos (Vec3): Position of the critter.
            food_pos (Vec3): Position of the food.
            threshold (float): Distance within which touching is detected.
    
        Returns:
            bool: True if touching, False otherwise.
        """
        distance = np.linalg.norm(
            np.array([critter_pos.getX(), critter_pos.getY()]) -
            np.array([food_pos.getX(), food_pos.getY()])
        )
        return distance <= threshold


    def evaluate_round(self):
        """Evaluate critter fitness based on their interactions."""
        print("Evaluating critters...")

        # Update critter positions from physics nodes
        for critter in self.critters:
            critter.position = critter.node.get_pos()
            print(f"  - Critter {critter.id}: Position updated to {critter.position}")

        for critter in self.critters:
            # Reset fitness for the round
            critter.fitness = 0

            # Iterate over a copy of food_items to allow safe removal
            for food in self.food_items[:]:
                if self.is_touching(critter.position, food.getPos()):
                    print(f"  - Critter {critter.id} touched food at {food.getPos()}. Incrementing fitness.")
                    food.removeNode()
                    self.food_items.remove(food)

                    # Increment fitness randomly between 0.5 and 1.0
                    fitness_gain = random.uniform(0.5, 1.0)
                    critter.fitness += fitness_gain
                    print(f"    > Fitness increased by {fitness_gain:.2f}. Total fitness: {critter.fitness:.2f}")
        print("Finished evaluating critters.")


    def reproduce_round(self):
        """Handle reproduction and replace less-fit critters."""
        print("Handling reproduction...")

        # Sort critters by fitness
        self.critters.sort(key=lambda c: c.fitness, reverse=True)
        print("  - Critters sorted by fitness.")

        # Select the top critters for reproduction
        top_critters = self.critters[:len(self.critters) // 2]
        print(f"  - Top {len(top_critters)} critters selected for reproduction.")

        # Generate offspring to replace the parents
        offspring = []
        for i in range(0, len(top_critters), 2):
            if i + 1 < len(top_critters):  # Ensure we have pairs
                parent1 = top_critters[i]
                parent2 = top_critters[i + 1]
                child = self.create_offspring(parent1, parent2)
                offspring.append(child)
                print(f"    > Offspring created from Critter {parent1.id} and Critter {parent2.id}.")

        # Replace the population with offspring
        self.critters = offspring
        print(f"Reproduction complete. New population size: {len(self.critters)}.")

              
    def create_offspring(self, parent1, parent2):
        """Create an offspring critter using two parents."""
        print(f"Creating offspring from parents {parent1.id} and {parent2.id}...")

        new_genes = []
        for gene1, gene2 in zip(parent1.genes, parent2.genes):
            new_gene = gene1.crossover(gene2)
            new_gene.mutate()
            new_genes.append(new_gene)

        # Spawn the offspring near one of the parents
        x = (parent1.position[0] + parent2.position[0]) / 2 + random.uniform(-10, 10)
        y = (parent1.position[1] + parent2.position[1]) / 2 + random.uniform(-10, 10)
        offspring = Critter(position=(x, y, 0), genes=new_genes)

        print(f"  - Offspring created at position ({x:.2f}, {y:.2f}).")
        return offspring


    def advance_round_phase(self, task):
        """Advance to the next phase in the round lifecycle."""
        self.round_manager.next_phase()
        return task.again
    
    def start_round_manager(self):
        """Kick off the round lifecycle using the RoundManager."""
        print("Starting the first round...")
        self.round_manager.trigger_phase_start()  # Start the first phase


app = BaseApp()
app.run()