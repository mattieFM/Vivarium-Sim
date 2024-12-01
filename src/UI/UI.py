"""
This module defines the UI class, responsible for managing and rendering a user interface with configurable options.
The UI class allows for adding, updating, and rendering configurable values, handling interactions with these options 
and updating the UI components dynamically.

Classes:
    UI: A class that manages and renders the user interface by handling configurable values and their associated actions.

"""


from UI.ConfigurableValue import UI_X_WIDTH, UI_Y_WIDTH

class UI():
    """
    A class for managing and rendering a user interface with configurable values.

    The UI class provides methods to add configurable options, update the UI components, 
    and render or unfocus all UI elements. It allows the addition of individual options 
    to the user interface and handles the display of these options in a vertical layout.

    Attributes:
        VERTICAL_SPACING_BETWEEN_OPTIONS (float): The vertical space between UI options.
        configurable_values (list): A list of ConfigurableValue objects that represent the configurable options in the UI.

    Methods:
        __init__: Initializes the UI instance and sets up the base options.
        add_base_options: Adds the initial set of base options to the UI.
        add_option: Adds a configurable option to the UI and triggers an update and rendering.
        update: Destroys all displayed config options and redraws them.
        unfocus_all: Unfocuses all configurable options that can be unfocused.
        setup: Renders all UI elements based on the list of configurable options.
    """
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