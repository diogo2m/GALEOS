from galeos.component_manager import ComponentManager


class User(ComponentManager):
    _instances = []
    _object_count = []
    
    def __init__(
            self,
            id : int = 0
        ):
        
        # Adding the object to the instance list
        self.__class__._instances.append(self) 
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id
        
        # User applications
        self.applications = []
        
        # User coordinates
        self.coordinates_trace = []
        self.coordinates = None
        
        # User mobility model
        self.mobility_model = None
        self.mobility_model_parameters = {}
        
        # User application access model
        self.applications_access_model = None
        self.applications_access_model_parameters = {}
        
        self.making_requests = {}
        
        self.communication_paths = {}
        self.delays = {}
        
        
    def set_mobility_model(self, model : callable, parameters : dict) -> None:
        self.mobility_model = model
        self.mobility_model_parameters = parameters
        
        
    def connection_to_application(self, app : object) -> None:
        self.applications.append(app)
        self.making_requests[app.id] = {}
        self.communication_paths[app.id] = []
        self.delays[app.id] = float('inf')
        
    
    def set_communication_path(self, application):
        # Quando completar a topologia 
        pass
        
        
        