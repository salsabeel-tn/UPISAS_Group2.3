from abc import ABC, abstractmethod
import requests
import pprint 
import requests
import time
import json
import random

from UPISAS.exceptions import EndpointNotReachable
from UPISAS.knowledge import Knowledge
from UPISAS import validate_schema, get_response_for_get_request
import logging

pp = pprint.PrettyPrinter(indent=4)

# Define an abstract base class for monitor and execute
class Strategy(ABC):

    def __init__(self, exemplar):
        """
        Initialize the strategy with a given exemplar and knowledge.
        `exemplar` is expected to contain configuration details like `base_endpoint`.
        """
        self.exemplar = exemplar  # Contains base_endpoint and other configurations
        self.knowledge = Knowledge(
            monitored_data={}, analysis_data={}, plan_data={},
            adaptation_options={}, monitor_schema={}, execute_schema={}, adaptation_options_schema={}
        )

    def ping(self):
        ping_res = self._perform_get_request(self.exemplar.base_endpoint)
        logging.info(f"ping result: {ping_res}")

    def monitor(self, endpoint_suffix="monitor", with_validation=True, verbose=False):
        """
        Fetch and process monitoring data from the `monitor` endpoint.

        Args:
            endpoint_suffix: Suffix of the endpoint to fetch monitoring data from.
            with_validation: Whether to validate the data against a schema.
            verbose: Print detailed information for debugging purposes.

        Returns:
            True if monitoring data is successfully fetched and processed.
        """
        fresh_data = self._perform_get_request(endpoint_suffix)
        if verbose:
            print("[Monitor]\tgot fresh_data: " + str(fresh_data))
        if with_validation:
            # Validate the fetched data against the monitoring schema
            if not self.knowledge.monitor_schema:
                self.get_monitor_schema()
            validate_schema(fresh_data, self.knowledge.monitor_schema)
        
        # Add QoS data to each snapshot
        for service_data in fresh_data.values():
            snapshots = service_data.get('snapshot', [])
            for snapshot in snapshots:
                if service_data.get('serviceId') in ["CONFIG-SERVER", "API-GATEWAY-SERVICE"]:
                    availability = None
                    response_time = None
                    snapshot['qos'] = {
                        'availability': availability,
                        'responseTime': response_time
                    }
                else:
                    # Assign random QoS metrics for other services
                    availability = random.randint(80, 90)
                    response_time = random.randint(2, 5)
                    snapshot['qos'] = {
                        'availability': availability,
                        'responseTime': response_time
                    }
        
        # Update the monitored data in the knowledge base
        self.knowledge.monitored_data = fresh_data  # Overwrite with fresh data
        if verbose:
            print("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))
            # print(str(self.knowledge))
        return True

    def execute(self, adaptation=None, endpoint_suffix="execute", with_validation=False):
        """
        Execute the given adaptation plan by posting it to the `execute` endpoint.

        Args:
            adaptation: The plan to execute (default is `self.knowledge.plan_data`).
            endpoint_suffix: Endpoint to send the adaptation data to.
            with_validation: Whether to validate the adaptation data before sending it.

        Returns:
            True if all adaptation requests are successfully executed.
        """
        # validation is dummy
        if not adaptation:
            adaptation = self.knowledge.plan_data
        if with_validation:
            if not self.knowledge.execute_schema:
                self.get_execute_schema()
            validate_schema(adaptation, self.knowledge.execute_schema)
        url = '/'.join([self.exemplar.base_endpoint.rstrip('/'), endpoint_suffix.lstrip('/')])
        
        # Send each request in the adaptation plan to the `execute` endpoint
        for request_item in adaptation.get("requests", []):
            response = requests.post(url, json=request_item)
            logging.info("[Execute]\tposted adaptation: " + str(request_item))

            # Handle potential errors in the response
            if response.status_code == 404:
                logging.error("Cannot execute adaptation on remote system, check that the execute endpoint exists.")
                raise EndpointNotReachable
            elif response.status_code >= 400:
                logging.error(f"Execute request failed with status code {response.status_code}: {response.text}")
                response.raise_for_status()
            else:
                logging.info(f"Execute request succeeded with status code {response.status_code}: {response.text}")

            print(response)

        return True

    def get_adaptation_options(self, endpoint_suffix="adaptation_options", with_validation=True):
        self.knowledge.adaptation_options = self._perform_get_request(endpoint_suffix)
        if with_validation:
            if not self.knowledge.adaptation_options_schema:
                self.get_adaptation_options_schema()
            validate_schema(self.knowledge.adaptation_options, self.knowledge.adaptation_options_schema)
        logging.info("adaptation_options set to: ")
        pp.pprint(self.knowledge.adaptation_options)

    def get_monitor_schema(self, endpoint_suffix="monitor_schema"):
        self.knowledge.monitor_schema = self._perform_get_request(endpoint_suffix)
        logging.info("monitor_schema set to: ")
        pp.pprint(self.knowledge.monitor_schema)

    def get_execute_schema(self, endpoint_suffix="execute_schema"):
        self.knowledge.execute_schema = self._perform_get_request(endpoint_suffix)
        logging.info("execute_schema set to: ")
        pp.pprint(self.knowledge.execute_schema)

    def get_adaptation_options_schema(self, endpoint_suffix="adaptation_options_schema"):
        self.knowledge.adaptation_options_schema = self._perform_get_request(endpoint_suffix)
        logging.info("adaptation_options_schema set to: ")
        pp.pprint(self.knowledge.adaptation_options_schema)
        
    def get_monitor_data(self):
        """
        Fetch monitoring data with retry logic for robustness.

        Returns:
            Parsed monitoring data or an empty JSON object if retries fail.
        """
        url = "http://127.0.0.1:41248/monitor"
        
        print("!!!!!!!!!!!!!!Config Server container is still starting, wait for 2 mins!!!!!!!!!!!!!!")
        time.sleep(120)  # Initial delay
        max_retries = 10  # Maximum number of retries
        delay_between_retries = 3  # Seconds to wait between retries
        timeout = 30  # Timeout for each request in seconds

        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} of {max_retries}")
                response = requests.get(url, timeout=timeout)  # Set timeout here
                if response.status_code == 200:
                    try:
                        data = response.json()  # Parse the JSON response
                        if data and len(data.keys()) != 1:  # Check if JSON is not empty
                            print("Response received successfully!")
                            print("Status Code:", response.status_code)
                            print("Response Content:", response.text)
                            return data  # Return the parsed JSON response
                        else:
                            print("Empty JSON response. Retrying...")
                    except ValueError:
                        print("Invalid JSON response. Retrying...")
                else:
                    print(f"Unexpected status code: {response.status_code}. Retrying...")
            except requests.exceptions.Timeout:
                print(f"Request timed out after {timeout} seconds. Retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying...")

            time.sleep(delay_between_retries)  # Wait before retrying

        print("Failed to fetch data after maximum retries.")
        
        return json.dumps({})

    def _perform_get_request(self, endpoint_suffix):
        """
        Perform a GET request to a given endpoint and handle errors.

        Args:
            endpoint_suffix: The suffix to append to the base endpoint for the GET request.

        Returns:
            The JSON response from the GET request.
        """
        if endpoint_suffix == "monitor":
            data = self.get_monitor_data()
            return data
        else:
            url = '/'.join([self.exemplar.base_endpoint.rstrip('/'), endpoint_suffix.lstrip('/')])
            response = get_response_for_get_request(url)
            if response.status_code == 404:
                logging.error(f"Endpoint '{endpoint_suffix}' not reachable at URL: {url}")
                raise EndpointNotReachable
            return response.json()

    @abstractmethod
    def analyze(self):
        """Implement the analysis logic specific to the strategy."""
        pass

    @abstractmethod
    def plan(self):
        """Implement the planning logic specific to the strategy."""
        pass 

