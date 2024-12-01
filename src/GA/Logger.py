class Logger():
    """the class for handling any and all logging that might need to be done"""
    
    def __init__(self, name, output_file):
        """setup the logger

        Args:
            name (_type_): _description_
            output_file (_type_): _description_
        """
        self.name = name
        self.output_file = output_file
        self.log_string = ""
        
    def log(self, str):
        """add a msg to the log"""
        self.log_string+=str
        
    def get_log(self):
        """get the string log"""
        return f"--{self.name} Start--\n"+self.log_string+"\n--{self.name} End--"
    
    def save(self,output_file=None):
        """save the log to file appending if file exists already

        Args:
            output_file (string, optional): path to save to if different than self. Defaults to self.output_file.
        """
        if(output_file == None): output_file = self.output_file
        with open(output_file, "a+") as file:
            file.write(self.get_log())
    
    
    