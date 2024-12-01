"""
CameraController Module

This module contains the `CameraController` class, which is responsible for managing 
camera movement and orientation in a 3D scene. The camera orbits around a central 
point (terrain center), with controls for rotation, zoom, and initial positioning.

Classes:
- `CameraController`: Handles camera controls, including rotation around a pivot 
  point, zooming, and setting up initial positions.

Key Features:
- Smooth camera rotation using user inputs for horizontal and vertical axes.
- Zoom functionality for adjusting the camera's distance from the orbit point.
- Dynamic adjustment of the camera's pivot point to align with the scene's center.

Dependencies:
- `CORE.util.Util`: Provides utility functions (e.g., clamping values).
- `panda3d.core.NodePath`: Used for managing 3D transformations and parenting.
- `direct.task.Task`: Enables task management for continuous camera updates.

Example Usage:
    from CameraController import CameraController

    camera_controller = CameraController(base, get_orbit_point, input, cam, taskMgr)
    camera_controller.setupCamControls()
"""


from CORE.util import Util
from panda3d.core import NodePath
from direct.task import Task

class CameraController():
    """
    CameraController

    This class manages the camera's movement and orientation within a 3D scene. 
    It allows the camera to orbit around a central pivot point, zoom in and out, 
    and initialize itself to a starting position relative to the scene.

    Attributes:
        VIEW_DISTANCE (float): The default distance from the camera to the orbit point.
        MIN_PITCH (int): The minimum pitch angle (in degrees) to restrict camera rotation.
        MAX_PITCH (int): The maximum pitch angle (in degrees) to restrict camera rotation.

    Args:
        base (BaseApp): The base application reference (e.g., Panda3D's ShowBase).
        get_orbit_point (Callable): A function returning the 3D point (Vec3) the camera orbits around.
        input (InputManager): Handles user input for camera control.
        cam (NodePath): The camera NodePath to control.
        taskMgr (TaskManager): Manages tasks for continuous camera updates.

    Methods:
        set_cam_origin_to_terrain_center():
            Repositions the camera's pivot point to the terrain center, enabling smooth rotation.
        
        setupCamControls():
            Initializes the camera controller and starts the camera update task.

        move_cam_task(task):
            Continuously updates the camera's position and orientation based on user input.

        move_cam_to_start_pos():
            Moves the camera to the starting position, looking down at the terrain center.
    """
    
    
    VIEW_DISTANCE = 1000
    """how far away from the focal point should we be to start out"""
    
    MIN_PITCH=0
    """what is the minimum pitch the user can view at"""
    
    MAX_PITCH=82
    """the max pitch the user can rotate to"""
    
    def __init__(self, base, get_orbit_point,input,cam,taskMgr):
        """

        Args:
            base (BaseApp): the base app reference
            orbit_point (Vec3): the point that this controller will rotate around
        """
        self.base = base
        """a reference to the BaseApp"""
        
        self.get_orbit_point = get_orbit_point
        """the function to get the orbit point, called each time we need to re reference"""
        
        self.input=input
        """reference to the input handler instance"""
        
        self.cam=cam
        """the camera """
        
        self.taskMgr=taskMgr
        """reference to the base app's  task_mgr"""
    
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
        """the task to move the camera"""
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