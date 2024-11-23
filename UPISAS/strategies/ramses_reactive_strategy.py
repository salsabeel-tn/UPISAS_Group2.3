from UPISAS.strategy import Strategy

#This is a port of the ReactiveAdaptationManager originally published alongside SWIM.
class ReactiveAdaptationManager(Strategy):
    def __init__(self, exemplar):
        """
        Initialize the ReactiveAdaptationManager with default configuration parameters and call the parent class initializer.

        Args:
            exemplar: Configuration object containing base endpoint and other settings.
        """
        super().__init__(exemplar)
        # Initialize RAMSES configuration parameters
        self.analysis_window_size = 5  # Example value
        self.metrics_window_size = 10  # Example value
        self.failure_rate_threshold = 0.1  # Example value
        self.unreachable_rate_threshold = 0.1  # Example value
        self.max_boot_time_seconds = 60  # Example value

    def analyze(self):
        """
        Analyze the monitored data to identify services violating QoS thresholds.

        Uses the `monitored_data` in knowledge to detect services with:
        - Availability below 85%
        - Response time above 3 seconds
        
        Updates `analysis_data` in the knowledge base with services requiring new instances.
        """
        try:
            print("Starting analysis phase.")
            monitored_data = self.knowledge.monitored_data
            analysis_data = {}

            # Iterate through the monitored data for each service
            for service_id, service_data in monitored_data.items():
                print(f"Analysing service {service_id}")
                current_implementation_id = service_data.get("currentImplementationId")

                # Assume instances and snapshots are available
                snapshots = service_data.get("snapshot", [])
                for snapshot in snapshots:
                    instance_id = snapshot.get("instanceId")
                    status = snapshot.get("status")
                    qos = snapshot.get("qos", {})

                    # Skip if instance is not active
                    if status != "ACTIVE":
                        print(f"Instance {instance_id} is not active (status: {status}). Skipping.")
                        continue

                    # Check for QOS violations
                    availability = qos.get("availability")
                    response_time = qos.get("responseTime")

                    # Convert availability to a number if it exists
                    if isinstance(availability, str) and availability.endswith("%"):
                        availability = float(availability.strip('%'))

                    """
                    If availability < 85% or response time > 3, add the currentImplementationId of the service
                    as a key in analysis_data with "addInstance" as its value.
                    """
                    if (availability is not None and availability < 85) or (response_time is not None and response_time > 3):
                        print(f"Instance {instance_id} of service {service_id} has QOS violation: "
                            f"Availability: {availability}, Response Time: {response_time}.")
                        
                        # Add to analysis_data
                        if current_implementation_id not in analysis_data:
                            analysis_data[current_implementation_id] = "addInstance"

            # Update knowledge with the analysis data
            self.knowledge.analysis_data = analysis_data
            print("Analysis phase completed. Analysis Data:", analysis_data)
            return True
        except Exception as e:
            print("Error during the Analyse execution:", str(e))
            return False
       
    def plan(self):
        """
        Generate a plan for adaptations based on the analysis results.

        Transforms `analysis_data` into `plan_data` that specifies the required actions for each service,
        such as adding new instances.
        """
        try:
            print("Starting plan phase.")
            
            # Extract analysis data
            analysis_data = self.knowledge.analysis_data
            
            # Prepare the plan data
            plan_data = {
                "requests": []
            }
            
            # Iterate through analysis_data and create request bodies
            for service_implementation_name, operation in analysis_data.items():
                if operation == "addInstance":
                    # Create a request to add an instance for the service
                    print(f"Adaptation for service {service_implementation_name} is needed, plan is being created with baseline strategy")
                    request_body = {
                        "operation": "addInstances",
                        "serviceImplementationName": service_implementation_name,
                        "numberOfInstances": 1
                    }
                    # Add the request to the list of planned actions
                    plan_data["requests"].append(request_body)

            # Update the knowledge base with the generated plan data
            self.knowledge.plan_data = plan_data
            print("Plan phase completed.")
            return True
        except Exception as e:
            print("Error during the Plan execution:", str(e))
            return False
