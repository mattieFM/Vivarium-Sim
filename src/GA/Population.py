class Population:
    """Class representing a collection of different critters"""
    
    def __init__(self):
        self.pop = []
        
    def get_population(self):
        return self.pop

    def add_to_population(self,element):
        self.pop.append(element)