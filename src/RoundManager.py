"""
Module for managing the lifecycle of a simulation round, including different phases like initialization, simulation, evaluation, and reproduction.

This module contains the `RoundManager` class, which is responsible for controlling the flow of a round in the simulation. It transitions through various phases and triggers actions associated with each phase. The `RoundManager` ensures that the simulation progresses according to predefined conditions, such as time limits and the state of food and critters in the environment.

Dependencies:
    - `GA.Food`: For accessing the food objects present in the simulation.
    - `GA.Critter`: For managing the critters and their statuses (e.g., whether they are alive or home).
    - `time`: For tracking the time spent in each phase of the simulation.

Classes:
    - `RoundManager`: Manages the round lifecycle and transitions between simulation phases.
"""
from GA.Food import Food
from GA.Critter import Critter

import time


class RoundManager:
    """
    Manages the lifecycle phases of a simulation round, including Initialization, Simulation, Evaluation, and Reproduction phases.

    Attributes:
        base_app (BaseApp): The main application that manages the simulation's behavior.
        population_cap (int): The maximum number of critters allowed in the simulation.
        current_phase_index (int): Index of the current phase (0 - Initialization, 1 - Simulation, 2 - Evaluation, 3 - Reproduction).
        round_count (int): The number of complete rounds (epochs) that have been executed.
        phase_start_time (float): The timestamp when the current phase started.
        phase_time_limit_seconds (int): The time limit (in seconds) for each phase before transitioning to the next.

    Methods:
        __init__(base_app, population_cap=100): Initializes a new round manager with a reference to the main app and optional population cap.
        is_no_more_food(): Checks if there is any food remaining on the map.
        all_alive_critters_are_home(): Checks if all critters have either returned home or been eaten.
        get_phase_time(): Returns the elapsed time since the current phase started.
        is_phase_over_the_time_limit(): Checks if the current phase has exceeded the time limit.
        is_simulation_phase_done(): Checks if the simulation phase should end based on food availability, time, and critter status.
        is_all_critters_at_home(): Checks if all critters are at the city (home).
        is_evaluation_phase_done(): Checks if the evaluation phase is over.
        is_reproduction_phase_done(): Checks if the reproduction phase is over.
        run_init_phase(): Starts the initialization phase and triggers the next phase.
        get_current_phase(): Returns the name of the current phase.
        next_phase(): Advances to the next phase in the cycle.
        trigger_phase_start(): Triggers the start of the current phase and calls the appropriate methods in the base app.
    """

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
