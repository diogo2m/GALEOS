from ...component_manager import ComponentManager
from ..network_flow import NetworkFlow

from itertools import cycle

class DynamicDurationAccessModel(ComponentManager):
    
    _instances = []
    _object_count = 0
    
    def __init__(
            self,
            user: object = None,
            application: object = None,
            start: int = 1,
            duration_values: list = [],
            connection_duration_values: list = [],
            interval_values: list = [],
            connection_interval_values: list = []
        ):
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1

        self.id = self.__class__._object_count
        
        self.duration_values = duration_values
        
        self.interval_values = interval_values
        
        self.connection_duration_values = connection_duration_values
        
        self.connection_interval_values = connection_interval_values
        
        self.history = []
        self.request_provisioning = False
        self.flow = None
        
        self.user = user
        self.application = application

        if application and user:
            self.get_next_access(start)
        
    def export(self) -> dict:
        component = {
            "id" : self.id,
            "history" : self.history,
            "request_provisioning" : self.request_provisioning,
            "duration_values" : self.duration_values,
            "interal_values" : self.interval_values,
            "connection_duration_values" : self.connection_duration_values,
            "connectin_interval_values" : self.connection_interval_values,
            "relationships" : {
                "user" : {'id' : self.user.id, 'class' : type(self.user).__name__} if self.user else None,
                "application" : {"id" : self.application.id, "class" : type(self.application).__name__} if self.application else None,
                "flow" : {"id" : self.flow.id, "class" : type(self.flow).__name__} if self.flow else None,
            }
        }
        
        return component
        
    def get_next_access(self, start):
        if not hasattr(self, 'duration_generator'):
            setattr(self, 'duration_generator', cycle(self.duration_values))
            
        if not hasattr(self ,'connection_duration_generator'):
            setattr(self, 'connection_duration_generator', cycle(self.connection_duration_values))
        
        if not hasattr(self,'interval_generator'):
            setattr(self, 'interval_generator', cycle(self.interval_values))
            
        if not hasattr(self, 'connection_interval_generator'):
            setattr(self, 'connection_interval_generator', cycle(self.connection_interval_values))
            
        interval = next(self.interval_generator)
        duration = next(self.duration_generator)
        
        connection_duration = next(self.connection_duration_generator)
        connection_interval = next(self.connection_interval_generator)
        
        making_request_times = {}
        request_time = start
        
        while request_time < start + duration:
            time = connection_duration if request_time + connection_duration < start + duration else duration - request_time
            for i in range( time):
                making_request_times[i + request_time] = True
                                
            request_time += time + connection_interval
            
            connection_duration = next(self.connection_duration_generator)
            connection_interval = next(self.connection_interval_generator)
        
        self.history.append({
            'start': start,
            'provisioned_time': 0,
            'required_provisioning_time' : duration,
            'waiting_provisioning': 0,
            'access_time': 0,
            'connection_failure_time': 0,
            'making_request': making_request_times,
            'next_access' : start + duration + interval,
        })
        
    
    def update_access(self) -> None:
        app = self.application    
        current_access = self.history[-1] 
            
        # If the application requests provisioning, update the metrics.   
        if self.request_provisioning:
            if app.available:
                current_access['provisioned_time'] += 1
                    
                if current_access['making_request'].get(str(self.model.scheduler.steps)):
                        
                    if self.flow.status == 'active':
                            current_access['access_time'] += 1
                        
                    else:
                        current_access['connection_failure_time'] += 1
            else:
                current_access['waiting_provisioning'] += 1
                    
       
        elif self.flow is not None:
            self.flow.status = 'finished'
            self.flow.end = self.model.scheduler.steps

            self.flow = None
                
        # Sets the flag value according to the model
        if current_access['start'] == self.model.scheduler.steps + 1:
            self.request_provisioning = True
                
                    
        elif current_access['end'] == self.model.scheduler.steps + 1:
            self.request_provisioning = False
                
            if self.flow is not None:
                self.flow.sapplicationtatus = "finished"
                    
            self.flow = None

            # Gets the next access according to the model since the current one has ended.
            self.get_next_access(current_access['next_access'])
                
        if current_access['making_request'].get(str(self.model.scheduler.steps + 1)):
            if self.flow is not None:
                if self.flow.target != app.process_unit or app.process_unit.available:
                    if not self.flow is None:
                        self.flow.status = 'finished'
                        self.flow = None
                        
            if self.flow is None:
                flow = NetworkFlow(
                    status="waiting",
                    start=self.model.scheduler.steps + 1,
                    source=self,
                    target=app.process_unit,
                    data_to_transfer=current_access.get('data_to_transfer', 1),
                    metadata={'type' : 'request_response', 'user' : self}
                )
                    
                self.flow = flow
