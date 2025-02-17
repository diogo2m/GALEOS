# Simulator components
from .components import*

# Python modules
from typing import Callable
import gzip
import json
import os

TIME_UNITS = [
    # add supported time units
]

class Simulator(ComponentManager):
    _instances = []
    _object_count = 0
    
    def __init__(
        self,
        id : int = 0,
        stopping_criterion : Callable = None,
        resource_management_algorithm : Callable = None,
        resource_management_algorithm_parameters : dict = {},
        topology_management_algorithm : Callable = None,
        topology_management_algorithm_parameters : dict = {},
        user_defined_functions : list = [],
        tick_duration : int = 1,
        tick_unit : str = "seconds",
        scheduler : Callable = DefaultScheduler, 
        dump_interval : int = 100,
        logs_directory : str = "logs",
        ignore_list : list = [], # Lista de componentes que n deve coletar metricas
        clean_data_in_memory : bool = False
        ) -> object:
        """ Method that creates the simulator  
        
        """
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id 
        
        self.stopping_criterion = stopping_criterion
        self.running = False
        
        self.resource_management_algorithm = resource_management_algorithm
        self.resource_management_algorithm_parameters = resource_management_algorithm_parameters
        
        self.topology_management_algorithm = topology_management_algorithm
        self.topology_management_algorithm_parameteres = topology_management_algorithm_parameters
        
        self.scheduler = scheduler
        self.topology = None
        
        self.logs_directory = logs_directory
        self.dump_interval = dump_interval
        self.last_dump = 0
        self.clean_data_in_memory = clean_data_in_memory
        
        # TODO: Customize the time unit
        
        for function in user_defined_functions:
            globals()[function.__name__] = function
        
        self.agent_metrics = {}
        self.ignore_list = ignore_list
        
        ComponentManager.model = self
    
    def initialize(self, dataset : str):
        for component_class in ComponentManager.__subclasses__():
            if component_class.__name__ != "Simulator":
                globals()[component_class.__name__].clear()
        
        with open(dataset, 'r', encoding='UTF-8') as file:
            dataset = json.load(file)
            
        created_components = []
        
        # Creates objects according to the dataset 
        for class_name, components in dataset.items():
            for component in components:
                obj = globals()[class_name]()
                
                obj.set_attributes(**component)
             
                obj.relationships = component["relationships"]
                
                created_components.append(obj)
                
        # Configures the relationships between objects 
        for obj in created_components:
            for key, value in obj.relationships.items():
                # If it's a function (e.g. mobility model, power consumption model)
                if type(value) == str and globals().get(value): 
                    setattr(obj, key, globals()[value])
                    
                # If it's as object of another class (e.g. applications)
                elif type(value) == dict and "class" in value and "id" in value: 
                    object_relation = globals()[value['class']].find_by("id", value['id'])
                    
                    setattr(obj, key, object_relation)

                # If it's a list of objects of another class
                elif type(value) == list and all(('id' in comp and 'class' in comp for comp in value)): 
                    components = [
                        globals()[component['class']].find_by('id', component['id']) for component in value 
                    ]

                    setattr(obj, key, components)

                elif value is None: 
                    setattr(obj, key, None)

        
        self.topology = Topology()
        
        for link in NetworkLink.all():
            topology.add_node(link["nodes"][0])
            topology.add_node(link["nodes"][1])
            
            topology.add_edge(link["nodes"])
            
            topology._adj[link.nodes[0]][link.nodes[1]] = link
            topology._adj[link.nodes[1]][link.nodes[0]] = link
        
        def initialize_logs(self) -> None:
            for component_class in ComponentManager.__subclasses__():
                if component_class not in self.ignore_list  + [self.__class__]:
                    pass
                    
            
        def step(self) -> None:
            # Updating satellite networks
            self.topology_management_algorithm(self.topology_management_parameters)
                
            self.scheduler.step()
            
        
        def monitor(self) ->None:
            """ Method that collects from components
            """
            for component_class in ComponentManager.__subclasses__():
                if component_class not in self.ignore_list  + [self.__class__]:
                    if component_class.__name__ not in self.agent_metrics:
                        self.agent_metrics[component_class.__name__] = {}
                        
                        metrics = []
                        
                        for component in component_class.all():
                            metrics.append(component.collect())
                            
                        self.agent_metrics[component_class.__name__][self.schedule.steps] = metrics
            
            if self.schedule.steps == self.last_dump + self.dump_interval:
                self.dump_data()
                self.last_dump = self.schedule.steps
                            
                            
        def dump_data(self) -> None:
            if not os.path.exists(f"{self.logs_directory}/"):
                os.makedirs(f"{self.logs_directory}")  
            
            for agent_class, value in self.agent_metrics.items():
                # TODO :  Discuss how to save the files (e.g. json, json+gzip, msgpack)
                pass
            
                if self.clean_data_in_memory:
                    self.agent_metrics[agent_class.__name__] = {}
            
        
        def run(self) -> dict:
            """ Execute the model
            """
            self.running = True
            
            while self.running:
                self.step()

                self.monitor()

                self.running = False if self.stopping_criterion(self) else True
            
            self.dump_data()
        

            
                            
                        
        
