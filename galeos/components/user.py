from ..component_manager import ComponentManager

from .network_flow import NetworkFlow

import networkx as nx

class User(ComponentManager):
    _instances = []
    _object_count = 0
    
    def __init__(
            self,
            id : int = 0,
            coordinates : tuple = None,
            max_connection_range : int = 500
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
        self.coordinates = coordinates
        
        # User mobility model
        self.mobility_model = None
        self.mobility_model_parameters = {}
        
        # User application access model
        self.applications_access_models = []
        
        self.network_access_points = []

        self.max_connection_range = max_connection_range
        
        
    def step(self):
        # Updates the information for each application access model
        for access_model in self.applications_access_models:   
            app = access_model.application    
            current_access = access_model.history[-1] 
            
            # If the application requests provisioning, update the metrics.   
            if access_model.request_provisioning:
                if app.available:
                    current_access['provisioned_time'] += 1
                    
                    if current_access['making_request'].get(str(self.model.scheduler.steps)):
                        
                        if access_model.flow.status == 'active':
                            current_access['access_time'] += 1
                        
                        else:
                            current_access['connection_failure_time'] += 1
                else:
                    current_access['waiting_provisioning'] += 1
                    
       
            elif access_model.flow is not None:
                access_model.flow.status = 'finished'

                access_model.flow = None
                
            # Sets the flag value according to the model
            if current_access['start'] == self.model.scheduler.steps + 1:
                access_model.request_provisioning = True
                
                    
            elif current_access['end'] == self.model.scheduler.steps + 1:
                access_model.request_provisioning = False
                
                if access_model.flow is not None:
                    access_model.flow.status = "finished"
                    
                access_model.flow = None

                # Gets the next access according to the model since the current one has ended.
                access_model.get_next_access(current_access['next_access'])
                
            if current_access['making_request'].get(str(self.model.scheduler.steps + 1)):
                if access_model.flow is not None:
                    # print(access_model.flow.path[0] if access_model.flow.path else None)
                    if access_model.flow.target != app.process_unit or app.process_unit.available:
                        if not access_model.flow is None:
                            access_model.flow.status = 'finished'
                            access_model.flow = None
                        
                if access_model.flow is None:
                    flow = NetworkFlow(
                        status="waiting",
                        start=self.model.scheduler.steps + 1,
                        source=self,
                        target=app.process_unit,
                        data_to_transfer=current_access.get('data_to_transfer', 1),
                        metadata={'type' : 'request_response', 'user' : self}
                    )
                    
                    access_model.flow = flow
                   
        
        if len(self.coordinates_trace) <= self.model.scheduler.steps:
            self.mobility_model(self)
            
        if self.coordinates != self.coordinates_trace[self.model.scheduler.steps]:
            self.coordinates = self.coordinates_trace[self.model.scheduler.steps]
                            
        self.network_access_points = []
        
          
    def collect_metrics(self):
        """ Defines the object metrics collection
        """     
        
        accesses = []
        
        for access_model in self.applications_access_models:
            last_access = access_model.history[-1]
            
            accesses.append({
                "Application ID" : access_model.application.id,
                "Request Provisioning" : access_model.request_provisioning,
                "Making Request" : last_access['making_request'].get(self.model.scheduler.steps, False),
                "Connectivity" :  access_model.flow and access_model.flow.status == 'active',
                "Path" : [str(node) for node in access_model.flow.path] if access_model.flow else [], 
            })
        
        metrics = {
            "ID" : self.id,
            "Coordinates" : self.coordinates,
            "Access to Applications" : accesses,
            "Network Access Points" : [ str(access_point) for access_point in self.network_access_points]
        }    
        
        return metrics  
                    
        
    def export(self):
        attributes = {
            "id" : self.id,
            "coordinates" : self.coordinates,
            "mobility_model_parameters" : self.mobility_model_parameters ,
            "relationships" : {
                "mobility_model" : self.mobility_model.__name__ if self.mobility_model else None,
                "applications_access_models" : [{"class" : type(access_model).__name__, 'id' : access_model.id} for access_model in self.applications_access_models],
                "applications" : [{"class" : type(app).__name__, 'id' : app.id} for app in self.applications] 
            }
        }

        return attributes
        
    def set_mobility_model(self, model : callable, parameters : dict) -> None:
        self.mobility_model = model
        self.mobility_model_parameters = parameters
        
        
    def connection_to_application(self, application :object, access_model : object) -> None:
        access_model.application = application
        access_model.user = self
        
        application.user = self
        
        self.applications_access_models.append(access_model)
        
    
    
    def connect_to_access_point(self, access_point : object):
        self.network_access_points.append(access_point)
        access_point.users.append(self)
        
        
    