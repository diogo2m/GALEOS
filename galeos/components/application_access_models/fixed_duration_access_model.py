from ...component_manager import ComponentManager
from ..network_flow import NetworkFlow

from itertools import cycle

import networkx as nx

class FixedDurationAccessModel(ComponentManager):
    
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
            "interval_values" : self.interval_values,
            "connection_duration_values" : self.connection_duration_values,
            "connection_interval_values" : self.connection_interval_values,
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
            if self.connection_interval_values == []:
                print(self)
                exit()
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
                making_request_times[str(i + request_time)] = True
                                
            request_time += time + connection_interval
            
            connection_duration = next(self.connection_duration_generator)
            connection_interval = next(self.connection_interval_generator)

        self.history.append({
            'start': start,
            'end': start + duration,
            'provisioned_time': 0,
            'waiting_provisioning': 0,
            'access_time': 0,
            'connection_failure_time': 0,
            'making_request': making_request_times,
            'next_access' : start + duration + interval,
        })

    
    def update_access(self) -> None:
        user = self.user
        app = self.application    
        current_access = self.history[-1] 
        
        if current_access['making_request'].get(str(self.model.scheduler.steps)):
            if self.flow is not None:
                if self.flow.target != app.process_unit:
                    self.flow.status = 'finished'
                    self.flow = None
                        
            if self.flow is None:
                
                connection_paths = []
                
                for access_point in user.network_access_points:
                    if nx.has_path(G=self.model.topology, source=access_point, target=app.process_unit):
                        path = nx.shortest_path(
                            G=self.model.topology,
                            source=access_point, 
                            target=app.process_unit,
                            weight='delay'
                        )
                                
                        connection_paths.append(path)
                    
                path = min(connection_paths, key=lambda path: len(path), default=[])
                
                flow = NetworkFlow(
                    start=self.model.scheduler.steps + 1,
                    source=self.user,
                    target=app.process_unit,
                    path=path,
                    data_to_transfer=current_access.get('data_to_transfer', 1),
                    metadata={'type' : 'request_response', 'user' : self.user}
                )
                    
                self.flow = flow