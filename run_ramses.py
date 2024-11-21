from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.ramses import RAMSES
import signal
import sys
import time

if __name__ == '__main__':
    try:
        exemplar = RAMSES(auto_start=True) #start containers
        time.sleep(3)
        exemplar.start_run() #run api.py
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