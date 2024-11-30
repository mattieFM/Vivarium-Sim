from panda3d.core import KeyboardButton
from direct.showbase.DirectObject import DirectObject

class Input(DirectObject):
    """the class that handles all input management in the game

    """
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