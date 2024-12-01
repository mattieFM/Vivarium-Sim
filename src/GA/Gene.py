import random

class Gene:
    """Class representing a single gene in a critter's genetic makeup."""
    genes = []

    def __init__(self, name, value, min_value=None, max_value=None, mutation_rate=0.5, mutation_step=0.1,
                 options=None, dominance=1, generation=0, parent_ids=None):
        """
        Initialize a new gene with its properties.
        
        Args:
            name (str): The name of the gene (something like "Strength").
            value (int, float, or str): The initial value of the gene.
            min_value (int or float, optional): Minimum value for the gene (if numeric).
            max_value (int or float, optional): Maximum value for the gene (if numeric).
            mutation_rate (float): Probability of mutation (0 to 1).
            mutation_step (float): Step size for numeric mutations.
            options (list, optional): Allowed values for categorical genes (if applicable).
            dominance (int, optional): Priority for crossover (higher value dominates).
            generation (int, optional): Generation in which this gene was created.
            parent_ids (list, optional): List of parent gene names for lineage tracking.
        """
        self.name = name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.mutation_rate = mutation_rate
        self.mutation_step = mutation_step
        self.options = options or []  # For categorical genes
        self.dominance = dominance
        self.generation = generation
        self.parent_ids = parent_ids or []
        self.active = True  # By default, the gene is active
        
        #if it does not already exist in genes
        if(not any(gene.name == self.name for gene in Gene.genes)):
            Gene.genes.append(self)
        
    def apply(self,critter):
        """this is used to apply the changes to a critter's stats 

        Args:
            critter (_type_): _description_
        """
        setattr(critter,self.name,self.value)

    def mutate(self):
        """
        Mutate the gene's value based on its mutation rate and step size.
        
        Numeric genes are incremented/decremented within their bounds.
        Categorical genes are randomly changed within their options.
        """
        if not self.active:
            return  # Skip mutation if the gene is inactive

        if random.random() < self.mutation_rate:  # Check if mutation occurs
            if isinstance(self.value, (int, float)):  # Numeric mutation
                mutation = random.uniform(-self.mutation_step, self.mutation_step)
                new_value = self.value + mutation
                if self.min_value is not None and self.max_value is not None:
                    self.value = max(self.min_value, min(new_value, self.max_value))
                else:
                    self.value = new_value
            elif isinstance(self.value, str) and self.options:  # Categorical mutation
                self.value = random.choice(self.options)

    def crossover(self, other):
        """
        Perform crossover with another gene to create an offspring gene.
        
        Args:
            other (Gene): The other parent gene.
        
        Returns:
            Gene: A new gene combining properties from both parents.
        """
        if not isinstance(other, Gene):
            raise ValueError("Crossover requires another Gene instance.")
        
        # Value inheritance based on dominance
        new_value = self.value if self.dominance >= other.dominance else other.value
        
        return Gene(
            name=self.name,
            value=new_value,
            min_value=self.min_value,
            max_value=self.max_value,
            mutation_rate=(self.mutation_rate + other.mutation_rate) / 2,
            mutation_step=(self.mutation_step + other.mutation_step) / 2,
            dominance=max(self.dominance, other.dominance),
            generation=max(self.generation, other.generation) + 1,
            parent_ids=[self.name, other.name]
        )

    def decay(self, rate=0.01):
        """
        Simulate gene decay by gradually decreasing its value.
        
        Args:
            rate (float): The rate of decay (default is 0.01).
        """
        if isinstance(self.value, (int, float)):
            self.value = max(self.min_value, self.value - rate)

    def __str__(self):
        """Return a string of the gene."""
        return (f"Gene(Name={self.name}, Value={self.value}, Min={self.min_value}, Max={self.max_value}, "
                f"MutationRate={self.mutation_rate}, MutationStep={self.mutation_step}, "
                f"Dominance={self.dominance}, Generation={self.generation})")