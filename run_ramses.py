from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.ramses_strategy import RamsesStrategy
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.ramses import RAMSES
import signal
import sys
import time

# class RamsesStrategy(RamsesStrategy):
#     def __init__(self, exemplar):
#         super().__init__(exemplar)

#     def analyze(self):
#         # Minimal implementation (add your logic here if needed)
#         print("[Analyze] No custom logic implemented.")

#     def plan(self):
#         # Minimal implementation (add your logic here if needed)
#         print("[Plan] No custom logic implemented.")


if __name__ == '__main__':
    try:
        exemplar = RAMSES(auto_start=True) #start containers
        time.sleep(3)
        exemplar.start_run() #run api.py
        
        print('sleeping')
        # Initialize the Strategy directly
        # strategy = RamsesStrategy(exemplar)
        strategy = ReactiveAdaptationManager(exemplar)
        # Invoke the monitor method
        strategy.monitor(verbose=True)
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)
  
    # try:
    #     strategy = ReactiveAdaptationManager(exemplar)

    #     strategy.get_monitor_schema()
    #     strategy.get_adaptation_options_schema()
    #     strategy.get_execute_schema()

    #     while True:
    #         input("Try to adapt?")
    #         strategy.monitor(verbose=True)
    #         if strategy.analyze():
    #             if strategy.plan():
    #                 strategy.execute()
            
    # except (Exception, KeyboardInterrupt) as e:
    #     print(str(e))
    #     input("something went wrong")
    #     exemplar.stop_container()
    #     sys.exit(0)