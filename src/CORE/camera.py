from CORE.util import Util
from panda3d.core import NodePath
from direct.task import Task

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