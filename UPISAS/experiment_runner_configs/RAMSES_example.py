from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, Optional
from pathlib import Path
from os.path import dirname, realpath
import time

from UPISAS.strategies.ramses_reactive_strategy import ReactiveAdaptationManager
from UPISAS.exemplars.ramses import RAMSES


class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER-SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name: str = "ramses_runner_experiment"

    """Output path for experiment results."""
    results_output_path: Path = ROOT_DIR / 'experiments'

    """Experiment operation type (e.g., manual or automatic runs)."""
    operation_type: OperationType = OperationType.AUTO

    """Cooldown period between runs (in milliseconds)."""
    time_between_runs_in_ms: int = 1000

    exemplar = None
    strategy = None

    def __init__(self):
        """Executes on program start and config load."""
        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment)
        ])
        self.run_table_model = None  # Initialized in `create_run_table_model`
        output.console_log("RAMSES Config loaded successfully")

    def create_run_table_model(self) -> RunTableModel:
        """Define the run table model with factors and data columns."""
        factor1 = FactorModel("failure_threshold", [0.1, 0.2, 0.3])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            exclude_variations=[],
            data_columns=['utility', 'failure_rate']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Execute actions before starting the experiment."""
        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Prepare the system before starting a run."""
        self.exemplar = RAMSES(auto_start=True)
        self.strategy = ReactiveAdaptationManager(self.exemplar)
        time.sleep(30)  # Allow the exemplar to initialize
        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        """Initialize parameters and start the target system for measurement."""
        self.strategy.failure_rate_threshold = float(context.run_variation['failure_threshold'])
        self.exemplar.start_run()
        time.sleep(3)  # Allow time for stabilization
        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        """Start performance measurement."""
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Interact with the system during the experiment."""
        time_slept = 0
        self.strategy.get_monitor_schema()
        self.strategy.get_adaptation_options_schema()
        self.strategy.get_execute_schema()

        while time_slept < 10:  # Example duration for interaction loop
            self.strategy.monitor(verbose=True)
            if self.strategy.analyze():
                if self.strategy.plan():
                    self.strategy.execute()

            time.sleep(3)
            time_slept += 3

        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        """Stop measurements after the interaction phase."""
        output.console_log("Config.stop_measurement() called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Stop the system and clean up resources after a run."""
        self.exemplar.stop_container()
        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Process and return collected data for the current run."""
        output.console_log("Config.populate_run_data() called!")

        monitored_data = self.strategy.knowledge.monitored_data
        utilities = []
        failure_rates = []

        print("MONITORED DATA:")
        print(monitored_data)

        for service_id, service_data in monitored_data.items():
            snapshots = service_data.get("snapshot", [])
            for snapshot in snapshots:
                qos = snapshot.get("qos", {})
                failure_rate = qos.get("failureRate", 0)
                utility = qos.get("utility", 0)

                utilities.append(utility)
                failure_rates.append(failure_rate)

        # Populate the run table with calculated metrics
        return {
            "utility": utilities,
            "failure_rate": failure_rates
        }

    def after_experiment(self) -> None:
        """Finalize the experiment and perform post-experiment activities."""
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path: Path = None
