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
        Add services with QOS violations to analysis_data:
        - If availability < 85% or response time > 3, add the currentImplementationId of the service
          as a key in analysis_data with "addInstance" as its value.
        """
        print("Starting analysis phase.")
        monitored_data = self.knowledge.monitored_data
        analysis_data = {}

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

                if (availability is not None and availability < 85) or (response_time is not None and response_time > 3):
                    print(f"Instance {instance_id} of service {service_id} has QOS violation: "
                          f"Availability: {availability}, Response Time: {response_time}.")
                    
                    # Add to analysis_data
                    if current_implementation_id not in analysis_data:
                        analysis_data[current_implementation_id] = "addInstance"

        # Update knowledge with the analysis data
        self.knowledge.analysis_data = analysis_data
        print("Analysis phase completed. Analysis Data:", analysis_data)

    except Exception as e:
        print("Error during the Analyse execution:", str(e))
        return False


    # def analyze(self):
    #     try:
    #         """
    #         Perform the analysis phase of the MAPE-K loop. Use monitored data to generate analysis data.
    #         This should add to analysis_data dict 2 things: name of the service with QOS violation, 'addInstance' strategy
    #         {"currentImplementationID1": "addInstance",
    #         "currentImplementationID2": "addInstance"}
    #         """
    #         print("Starting analysis phase.")
    #         monitored_data = self.knowledge.monitored_data
    #         analysis_data = {}

    #         for service_id, service_data in monitored_data.items():
    #             print(f"Analysing service {service_id}")
    #             analysis_data[service_id] = {
    #                 "instances": [],
    #                 "forced_adaptations": [],
    #             }

    #             for instance in service_data.get("instances", []):
    #                 instance_id = instance.get("instance_id")
    #                 status = instance.get("status")

    #                 if status == "SHUTDOWN":
    #                     print(f"Instance {instance_id} is shutdown, ignoring.")
    #                     # self.services_to_skip.add(service_id)
    #                     continue

    #                 if status == "BOOTING":
    #                     print(f"Instance {instance_id} is booting, skipping further analysis.")
    #                     # self.services_to_skip.add(service_id)
    #                     continue

    #                 if status == "FAILED":
    #                     print(f"Instance {instance_id} failed. Forcing shutdown.")
    #                     analysis_data[service_id]["forced_adaptations"].append("ShutdownInstanceOption")
    #                     # self.services_to_skip.add(service_id)
    #                     continue

    #                 if status == "ACTIVE":
    #                     qos_values = instance.get("qos", {})
    #                     analysis_data[service_id]["instances"].append({
    #                         "instance_id": instance_id,
    #                         "qos_values": qos_values,
    #                     })
    #             # Check if there are no active instances
    #             if not analysis_data[service_id]["instances"]:
    #                 print(f"No active instances for service {service_id}. Adding an instance.")
    #                 analysis_data[service_id]["forced_adaptations"].append("AddInstanceOption")
    #                 # self.services_to_skip.add(service_id)

    #         self.knowledge.analysis_data = analysis_data
    #         print("Analysis phase completed.")

    #     except Exception as e:
    #         print("Error during the Analyse execution: %s", str(e))
    #         return False
       
    def plan(self):
        """
        Perform the planning phase of the MAPE-K loop. Use analysis data to generate plan data.
        """
        print("Starting plan phase.")
        analysis_data = self.knowledge.analysis_data
        plan_data = {}

        for service_id, service_analysis in analysis_data.items():
            forced_adaptations = service_analysis.get("forced_adaptations", [])
            if forced_adaptations:
                print(f"Service {service_id} has forced adaptations: {forced_adaptations}")
                plan_data[service_id] = forced_adaptations
                continue

            proposed_options = self.knowledge.adaptation_options.get(service_id, [])
            if proposed_options:
                best_option = self.select_best_option(service_id, proposed_options)
                if best_option:
                    plan_data[service_id] = [best_option]

        self.knowledge.plan_data = plan_data
        print("Plan phase completed.")