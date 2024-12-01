from GA.Food import Food
from GA.Critter import Critter

import time


class RoundManager:
    """Manages the lifecycle phases of a simulation round."""

    PHASES = ["Initialization", "Simulation", "Evaluation", "Reproduction"]

    def __init__(self, base_app, population_cap=100):
        """
        Initialize the round manager.

        Args:
            base_app (BaseApp): Reference to the main app.
            population_cap (int): Maximum number of critters allowed.
        """
        self.base_app = base_app
        self.current_phase_index = 0 # the current phase index 0-3
        self.round_count=0 #how many epoachs of all the phases have run
        self.population_cap = population_cap
        self.phase_start_time = time.time()
        self.phase_time_limit_seconds = 30
        
    def is_no_more_food(self):
        """is there any food left on the map

        Returns:
            _type_: _description_
        """
        return len(Food.foods)==0
    
    def all_alive_critters_are_home(self):
        """if all critters taht were not eated already returned home"""
        val = all(critter.at_city or critter.eaten for critter in Critter.critters)
        #print(f"all eaten or home: {val}")
        return val
    
    def get_phase_time(self):
        """get the amount of time in seconds since the start oof this round"""
        return time.time() - self.phase_start_time
    
    def is_phase_over_the_time_limit(self):
        return self.get_phase_time() > self.phase_time_limit_seconds
    
    def is_simulation_phase_done(self):
        """is it time to end the simulation phase
        sim phase ends when there is no more food or time as ran out
        """
        return (self.is_no_more_food() or self.is_phase_over_the_time_limit() or self.all_alive_critters_are_home()) and self.current_phase_index == 1
    
    def is_all_critters_at_home(self):
        return all(critter.at_city for critter in Critter.critters)
    
    def is_evaluation_phase_done(self):
        """is the evaluation phase over

        Returns:
            _type_: _description_
        """
        return (self.all_alive_critters_are_home() or self.get_phase_time() > self.phase_time_limit_seconds/5) and self.current_phase_index == 2
    
    def is_reproduction_phase_done(self):
        return self.current_phase_index == 3
        
    def run_init_phase(self):
        """set the current phase to initialization and run"""
        self.trigger_phase_start()

    def get_current_phase(self):
        """Return the current phase name."""
        return self.PHASES[self.current_phase_index]

    def next_phase(self):
        """Advance to the next phase in the cycle."""
        self.current_phase_index = (self.current_phase_index + 1) % len(self.PHASES)
        self.trigger_phase_start()

    def trigger_phase_start(self):
        """Trigger the start of the current phase."""
        self.phase_start_time = time.time()
        phase = self.get_current_phase()
        print(f"Starting Phase: {phase}")
        if phase == "Initialization":
            self.base_app.initialize_round()
            self.next_phase()
        elif phase == "Simulation":
            self.base_app.simulate_round()
        elif phase == "Evaluation":
            self.base_app.evaluate_round()
        elif phase == "Reproduction":
            self.base_app.reproduce_round()
            self.round_count+=1
