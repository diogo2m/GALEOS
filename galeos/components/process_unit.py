from galeos.component_manager import ComponentManager

class ProcessUnit(ComponentManager):
    
    _instances = []
    _object_count = 0
   
    def __init__(
            self,
            id : int = 0,
            cpu : int = 0,
            memory : int = 0,
            storage : int = 0,
            coordinates : tuple = None,
            model_name : str = "",
            architecture : dict = None
        ):
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id 
        
        self.model_name = model_name
        
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        
        self.cpu_demand = 0
        self.memory_demand = 0
        self.storage_demand = 0
        
        self.architecture = architecture
        
        self.power_generation_model = None
        self.power_generation_model_parameters = {}
        
        self.power_consumption_model = None
        self.power_consumption_model_parameters = {}
        
        self.failure_model = None
        self.failure_model_parameters = {}
        
        # Registries and applications hosted by the edge server
        self.registries = []
        self.applications = []
        
        # Network device to which the Process Unit is conneccted
        self.network_access_point = None
        
        # Edge server's availability status
        self.available = True

        # Dependency waiting queue
        self.waiting_queue = []
        
        # Dependency download queue
        self.download_queue = []
       
       
    def export(self) -> dict:
        """ Method that generates a representation of the object in dictionary format to save current context
        
        """
        component = {
            "id" : self.id,
            "cpu" : self.cpu,
            "memory" : self.memory,
            "storage" : self.storage,
            "model_name" : self.model_name,
            "architecture" : self.architecture,
            "coordinates" : self.coordinates,
            "coordinates_trace" : self.coordinates_trace,
            "available" : self.available,
            "power_generation_model_parameters" : self.power_generation_model_parameters,
            "power_consumption_model_parameters" :self.power_consumption_model_parameters,
            
            "relationships" :{
                "power_generation_model" : self.power_generation_model.__name__ if self.power_generation_model else None,
                "power_consumption_model" : self.power_consumption_model.__name__ if self.power_consumption_model else None,
                "failure_model" : self.failure_model.__name__ if self.failure_model else None,
                "network_access_point" : { "id" : self.network_access_point.id, "class" : self.network_access_point.__name__} if self.network_access_point else None,
                "registries" : [
                    {
                        "class" : registry.__name__,
                        "id" : registry.id
                    } for registry in self.registries
                ],
                "applications" : [
                    {
                        "class" : app.__name__,
                        "id" : app.id
                    } for app in self.applications
                ]
                
            }
        } 
        
        return component
    
    def provision(self, applications : object) -> None:
        pass