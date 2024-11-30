from UI.ConfigurableValue import UI_X_WIDTH, UI_Y_WIDTH

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