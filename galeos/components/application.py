# Simulator components
from galeos.component_manager import ComponentManager

from typing import List

class Application(ComponentManager):
    
    _instances = []
    _object_count = 0
    
    def __init__(
            self,
            id : int = None,
            cpu_demand : int = None,
            memory_demand : int = None,
            storage_demand : int = None,
            dependency_labels : List[str] = [],
            architectural_demands : dict = {},
            state : int = 0,
            sla : int = 0,
        ):
        
        # Adding the object to the instance list
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id 
        
        
        # Sets demands
        self.cpu_demand = cpu_demand
        self.memory_demand = memory_demand
        self.storage_demand = storage_demand
        
        # Set state
        self.state = state
        
        # Set SLA
        self.sla = sla
        
        # Set dependencies labels (e.g. containers, libraries, etc.) required to provision the application 
        self.dependency_labels = dependency_labels
        
        self.architectural_demands = architectural_demands
        
        self.user = None
        self.server = None
        
        self.migrations = []
        self._available = False  
        self.being_provisioned = False
        
        self.model = None
        
    
    def step(self):
        pass
    
    
    def export(self):
        pass
    
    def provision(self, server):
        pass
    
    
    
    
    