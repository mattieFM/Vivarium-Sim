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

    def get_current_phase(self):
        """Return the current phase name."""
        return self.PHASES[self.current_phase_index]

    def next_phase(self):
        """Advance to the next phase in the cycle."""
        self.current_phase_index = (self.current_phase_index + 1) % len(self.PHASES)
        self.trigger_phase_start()

    def trigger_phase_start(self):
        """Trigger the start of the current phase."""
        phase = self.get_current_phase()
        print(f"Starting Phase: {phase}")
        if phase == "Initialization":
            self.base_app.initialize_round()
        elif phase == "Simulation":
            self.base_app.simulate_round()
        elif phase == "Evaluation":
            self.base_app.evaluate_round()
        elif phase == "Reproduction":
            self.base_app.reproduce_round()
            self.round_count+=1
