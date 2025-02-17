# Simulator components
from galeos.component_manager import ComponentManager

from typing import List
import networkx as nx

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
        self.process_unit = None
        
        self.migrations = []
        self._available = False  
        self.being_provisioned = False
                
    
    def step(self):
       pass
    

    def export(self):
        """ Method that generates a representation of the object in dictionary format to save current context
        """
        return {
            "id" : self.id,
            "cpu_demand" : self.cpu_demand,
            "memory_demand" : self.memory_demand,
            "storage_demand" : self.storage_demand,
            "state" : self.state,
            "sla" : self.sla,
            "dependency_labels" : self.dependency_labels,
            "architectural_demands" : self.architectural_demands,
            "relationships" :{
                "user" : {"id" : self.user.id, "class" : type(self.user).__name__} if self.user else None,
                "process_unit" : {"id" : self.process_unit.id, "class" : type(self.process_unit).__name__} if self.process_unit else None,
            }
        }
    
    def provision(self, process_unit : object):
        # Enables the flag that the service is being provisioned
        self.being_provisioned = True
        
        
        process_unit.cpu_demand += self.cpu_demand
        process_unit.memory_demand += self.memory_demand
        
        self.migrations.append({
            "status" : "waiting",
            "origin" : self.process_unit,
            "target" : process_unit,
            "start" : self.model.schedule.steps + 1,
            "end" : None
        })
    
    
    
    