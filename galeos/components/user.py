from galeos.component_manager import ComponentManager


class User(ComponentManager):
    _instances = []
    _object_count = 0
    
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
        
        
    def export(self):
        return {
            "id" : self.id,
            "coordinates" : self.coordinates,
            "delays" : self.delays,
            "making_requests" : self.making_requests,
            "mobility_model_parameters" : self.mobility_model_parameters ,
            "applications_access_model_parameters" :  self.applications_access_model_parameters,
            "relationships" : {
                "mobility_model" : self.mobility_model.__name__,
                "application_access_model" : self.applications_access_model.__name__ ,
                "applications" : [{"class" : type(app).__name__, 'id' : app.id} for app in self.applications] 
            }
        }
        
        
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
        
        
        