import pprint, time
from UPISAS.exemplar import Exemplar
import logging
import os
import subprocess

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class RAMSES(Exemplar):
    """
    
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""
    def __init__(self, auto_start=True, container_name = "ramses"
                 ):
        self.base_endpoint = "http://127.0.0.1:41248"
        self.ramses_path = os.path.join(os.path.dirname(__file__), "..", "ramses")
        if auto_start:
            self.start_container()
    
    def start_run(self): 
        # to start the api from RAMES interface
        try:
            interface_path =  os.path.join(self.ramses_path, "interface")
            subprocess.Popen(
                [
                'python', '-m', 'flask',
                '--app', 'api',
                'run',
                '--host=0.0.0.0',
                '--port=41248'
                ],
                # ['python', 'api.py'],
                # ['python', '-m', 'flask', '--app', 'api', 'run', '--host=0.0.0.0', '--port=41248']
                cwd=interface_path
            )
            logging.info("API started successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start API: {e}")
            raise
    
    def start_container(self):
        try:
            subprocess.run(
                ['docker', 'compose', 'up', '-d'],
                cwd=self.ramses_path,
                check=True
            )
            logging.info("Docker Compose services started successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start Docker Compose: {e}")
            raise
    
    def stop_container(self):
        try:
            subprocess.run(
                ['docker', 'compose', 'down'],
                cwd=self.ramses_path,
                check=True
            )
            logging.info("Docker Compose services shut down successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to close Docker Compose: {e}")
            raise