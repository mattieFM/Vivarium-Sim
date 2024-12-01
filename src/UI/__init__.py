"""
UI

A small helper module for making the UI. This contains two classes
UI and its child ConfigurableValues which are used together to create simple modular
UIs

Usage:
    Example of a checkbox element:
    
    def edit_terrain_toggle(val):
            self.edit_terrain_enabled = val
    self.ui.add_option(ConfigurableValue(edit_terrain_toggle, "edit", True))
    
    Example of a entry element:
    
    def edit_radius(val):
            self.edit_radius = float(val)
            self.ui.unfocus_all()
    self.ui.add_option(ConfigurableValue(edit_radius, "edit radius", False, placeholder=self.edit_radius))
    
    Note the use of unfocus_all in the second example, the UI is greedy with its focus and
    once entered will not relinquish it on its own for entries, thus un_focus all must be used
    it can also be used in a recurring task to check as a timeout or something similar.
"""