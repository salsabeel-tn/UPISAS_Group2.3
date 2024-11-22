from UPISAS.strategy import Strategy

#This is a port of the ReactiveAdaptationManager originally published alongside SWIM.
class ReactiveAdaptationManager(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        # Initialize RAMSES configuration parameters
        self.analysis_window_size = 5  # Example value
        self.metrics_window_size = 10  # Example value
        self.failure_rate_threshold = 0.1  # Example value
        self.unreachable_rate_threshold = 0.1  # Example value
        self.qos_satisfaction_rate = 0.9  # Example value
        self.max_boot_time_seconds = 60  # Example value

    def analyze(self):
        try:
            """
            Perform the analysis phase of the MAPE-K loop. Use monitored data to generate analysis data.
            """
            print("Starting analysis phase.")
            monitored_data = self.knowledge.monitored_data
            analysis_data = {}

            for service_id, service_data in monitored_data.items():
                print(f"Analysing service {service_id}")
                analysis_data[service_id] = {
                    "instances": [],
                    "forced_adaptations": [],
                }

                for instance in service_data.get("instances", []):
                    instance_id = instance.get("instance_id")
                    status = instance.get("status")

                    if status == "SHUTDOWN":
                        print(f"Instance {instance_id} is shutdown, ignoring.")
                        self.services_to_skip.add(service_id)
                        continue

                    if status == "BOOTING":
                        print(f"Instance {instance_id} is booting, skipping further analysis.")
                        self.services_to_skip.add(service_id)
                        continue

                    if status == "FAILED":
                        print(f"Instance {instance_id} failed. Forcing shutdown.")
                        analysis_data[service_id]["forced_adaptations"].append("ShutdownInstanceOption")
                        self.services_to_skip.add(service_id)
                        continue

                    if status == "ACTIVE":
                        qos_values = instance.get("qos", {})
                        analysis_data[service_id]["instances"].append({
                            "instance_id": instance_id,
                            "qos_values": qos_values,
                        })
                # Check if there are no active instances
                if not analysis_data[service_id]["instances"]:
                    print(f"No active instances for service {service_id}. Adding an instance.")
                    analysis_data[service_id]["forced_adaptations"].append("AddInstanceOption")
                    self.services_to_skip.add(service_id)

            self.knowledge.analysis_data = analysis_data
            print("Analysis phase completed.")

        except Exception as e:
            print("Error during the Analyse execution: %s", str(e))
            return False
    
    def plan(self):
        """
        Transform analysis data into plan data with request bodies.
        """
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
                # Create a request body
                print(f"Adaptation for service {service_implementation_name} is needed, plan is being created with baseline strategy")
                request_body = {
                    "operation": "addInstances",
                    "serviceImplementationName": service_implementation_name,
                    "numberOfInstances": 1
                }
                # Append to the list of requests
                plan_data["requests"].append(request_body)
        # Update knowledge with the plan data
        self.knowledge.plan_data = plan_data
        print("Plan phase completed.")
        print(self.knowledge.plan_data)





    def plan(self):
        if((self.knowledge.analysis_data["rt_sufficient"])):
            if(self.knowledge.analysis_data["spare_utilization"] > 1):
                if(not(self.knowledge.analysis_data["dimmer_at_max"])):
                    self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"] + self.DIMMER_MARGIN
                    self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] #This is due to the schema validation checking for keys.
                    return True
                elif(not(self.knowledge.analysis_data["server_booting"]) and self.knowledge.analysis_data["is_server_removable"]):
                    self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] - 1
                    self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
                    return True

        else:
            self.knowledge.analysis_data["dimmer_at_min"]
            if(not(self.knowledge.analysis_data["server_booting"]) and (self.knowledge.analysis_data["server_room"])):
                self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] + 1
                self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
                return True
            elif(not(self.knowledge.analysis_data["dimmer_at_min"])):
                self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"] - self.DIMMER_MARGIN
                self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"]
                return True
            
        return False