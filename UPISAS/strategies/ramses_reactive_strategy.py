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

        # Internal state variables
        self.current_architecture_map: Dict[str, Service] = {}
        self.services_forced_adaptation_options_map: Dict[str, List[str]] = {}
        self.services_proposed_adaptation_options_map: Dict[str, List[str]] = {}
        self.services_to_skip: Set[str] = set()

    def analyze(self):
        try:
            monitored_data = self.knowledge.monitored_data
            print(monitored_data)
            # Get services map from monitored data
            monitored_data = self.knowledge.monitored_data
            self.current_architecture_map = self.get_services_map_from_monitored_data(monitored_data)
            # Perform analysis
            self.analyse()
            # Store adaptation options in analysis data
            self.knowledge.analysis_data['forced_adaptation_options'] = self.services_forced_adaptation_options_map
            self.knowledge.analysis_data['proposed_adaptation_options'] = self.services_proposed_adaptation_options_map
            print("Ending Analyse routine")
            return True
        except Exception as e:
            print("Error during the Analyse execution: %s", str(e))
            return False
    
    def get_services_map_from_monitored_data(self, monitored_data):
        services_map = {}
        services_data = monitored_data.get('services', {})
        for service_id, service_info in services_data.items():
            service = Service(service_id, service_info)
            services_map[service_id] = service
        return services_map



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