# Simulator components
from ..component_manager import ComponentManager
from .user import User

class Satellite(ComponentManager):
    _instances = []
    _object_count = 0
        
    def __init__(
            self, 
            id: int = 0,
            name: str = "",
            coordinates : tuple = None,
            wireless_delay : int = 0,
            max_connection_range : int = 500,
            is_gateway : bool = False
            
        ) -> object:
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id

        self.name = name if name else f"Satellite {id}"

        self.process_unit = None
        self.active = True
        self.wireless_delay = wireless_delay
        self.is_gateway = is_gateway
        self.users = []
        self.max_connection_range = max_connection_range
        self.power = 0
        self.min_power = 0

        
        # Satelite coordinates
        self.coordinates = coordinates
        self.coordinates_trace = []
        
        # Satelite models
        self.mobility_model = None
        self.mobility_model_parameters = {}
        
        self.power_generation_model = None
        self.power_generation_model_parameters = {}
        
        self.power_consumption_model = None
        self.power_consumption_model_parameters = {}
        
        self.failure_model = None
        self.failure_model_parameters = {}
        
        
    def collect_metrics(self) -> dict:
        metrics = {
            "ID" : self.id,
            "Coordinates" : self.coordinates,
            "Power" : self.power,
            "Active" : self.active,
            "Is Gateway" : self.is_gateway
        }
        
        return metrics
    
    
    def step(self) -> None:
        self.users = []
        self.mobility_model(self, **self.mobility_model_parameters)
        
        if self.process_unit:
            self.process_unit.coordinates =self.coordinates
            
        if self.coordinates is None:
            self.active = False
            
            if self.process_unit:
                self.process_unit.available
                
            return 
        
        failure_occurred = False
        
        # Check if there was a failure
        if self.failure_model:
            failure_occurred = self.failure_model(self, **self.failure_model_parameters)
            if failure_occurred:
                self.active = False
            else: 
                self.active = True
        
        power_generated = 0
        if self.power_generation_model:
            power_generated = self.power_generation_model(self, **self.power_generation_model_parameters)
        self.power += power_generated
        
        power_consumed = 0
        if self.power_consumption_model:
            power_consumed = self.power_consumption_model(self, **self.power_consumption_model_parameters)
        self.power -= power_consumed
        
        
        # Check the current power level
        if self.power < self.min_power:
            self.active = False
            
            if self.process_unit:
                self.process_unit.available = True
            
        elif not failure_occurred and not self.active:
            self.active = True
        
        if self.active:
            for user in User.all():
                if self.model.topology.within_range(self, user):
                    user.connect_to_access_point(self)
            
    def export(self):
        """ Method that generates a representation of the object in dictionary format to save current context
        """  
        component = {
            "id" : self.id,
            "coordinates" : self.coordinates,
            "active" : self.active,
            "power" : self.power,
            "min_power" : self.min_power,
            "wireless_delay" : self.wireless_delay,
            "is_gateway" : self.is_gateway,
            "max_connection_range" : self.max_connection_range,
            "mobility_model_parameters" : self.mobility_model_parameters,
            "power_consumption_model_parameters" : self.power_consumption_model_parameters,
            "power_generate_model_parameters" : self.power_generation_model_parameters,
            "failure_model_parameters" : self.failure_model_parameters,
            "relationships" : {
                "mobility_model" : self.mobility_model.__name__ if self.mobility_model else None,
                "power_consumption_model" : self.power_consumption_model.__name__ if self.power_consumption_model else None,
                "power_generate_model" : self.power_generation_model.__name__ if self.power_generation_model else None,
                "failure_model_parameters" : self.failure_model.__name__ if self.failure_model else None,
                "process_unit" : {
                    "id" : self.process_unit.id,
                    "class" : type(self.process_unit).__name__
                } if self.process_unit else None,
            }
        }
        
        return component
