import numpy as np
from direct.gui.DirectGui import *


#these values need to be replaces with runtime values
#right now they assume 3:4 aspect ratio
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