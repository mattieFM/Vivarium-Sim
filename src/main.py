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




#our imports
from CORE.util import Util
from GA.Gene import Gene
from RoundManager import RoundManager
from GA.Critter import Critter
from UI.ConfigurableValue import ConfigurableValue
from UI.UI import UI
from CORE.input import Input
from CORE.camera import CameraController
from CORE.Terrain import TerrainController
from CORE.entity import Entity
from GA.Food import Food

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
    
    critters = []
    
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
        #self.init_terrain()
        self.terrainController = TerrainController(self)

        #set up colliders and pickz_scaleer
        self.picker_setup()
        
        #set up bullet grav and phys engine
        self.init_gravity()
        
        #init our camera controller
        self.camera_controller = CameraController(
            self,
            self.terrainController.get_terrain_center,
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
        #self.taskMgr.add(self.terrain_update_task, "update")
        
        #this makes sure when we stop looking at the ui it becomes unfocused
        self.task_mgr.add(self.handle_unfocus, "handle_unfocus")
        
        #handles all terrain editing 
        #self.task_mgr.add(self.handle_terrain_edit, "handleEnvironmentChange")
        
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
        self.terrainController.create_heightFieldMap_Collider()
        
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
    
    def update_grav(self,task):
        """update the gravity phys of the world, use delta time to account for fps differences"""
        dt = globalClock.getDt()
        self.world.doPhysics(dt)
        #self.create_heightFieldMap_Collider()
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
                point = entry.getSurfacePoint(self.terrainController.terrain_np)
                callback(point)             
                
    def handle_unfocus(self,task):
        """a simple task called every frame, if either mouse button clicks outside of the UI unfocus all UI elements"""
        if(self.input.mouse_held or self.input.mouse3_held):
            self.ui.unfocus_all()
        return Task.cont
        
    
    def summon_critter(self, x, y, color=None):
        """a method to bring forth a phys enabled critter at chosen pos, height is automatic based on height map

        Args:
            x (float): _description_
            y (float): _description_
            color (tuple, optional): The color of the critter. Randomized if not provided.
        """
        # Load the visual model for the critter
        critter = Critter(base=self).spawn(x=x,y=y,color=color)

        print(f"Spawned {critter}")
        
    def set_critter_height(self,blob_np,x,y):
        """move a critter to the correct z height based on height map

        Args:
            blob_np (node): _description_
            x (_type_): _description_
            y (_type_): _description_

        Returns:
            float: new z pos
        """
        z = self.terrainController.heightmap.get_gray(int(x),int(np.abs(y - self.terrainController.heightmap.getYSize())))*self.z_scale+self.critter_offset_z+10
        blob_np.set_pos(x,y,z)
        return z
                
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
            x = random.uniform(0, self.terrainController.heightmap.getXSize())
            y = random.uniform(0, self.terrainController.heightmap.getYSize())
        
        food = Food(base=self).spawn(x=x,y=y)


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
            if critter.body_np:
                self.set_critter_height(critter.body_np, critter.position[0], critter.position[1])  # Reset positions
        print(f"{len(self.critters)} critters reset for the new round.")
        
    def spawn_initial_population(self, count=10):
        """Spawn an initial population of critters randomly within the terrain."""
        for _ in range(count):
            # Generate random positions on the map
            x = random.uniform(0, self.terrainController.heightmap.getXSize())
            y = random.uniform(0, self.terrainController.heightmap.getYSize())
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



# Entry point for the script
if __name__ == "__main__":
    app = BaseApp()
    app.run()