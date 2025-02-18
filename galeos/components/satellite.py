# Simulator components
from ..component_manager import ComponentManager

class Satellite(ComponentManager):
    _instances = []
    _object_count = 0
    
    def __init__(
            self, 
            id: int = 0,
            name: str = "",
            coordinates : tuple = None,
            wireless_delay : int = 0
            
        ) -> object:
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id

        self.name = name if name else f"Satellite {id}"

        self.links = []
        self.process_unit = None
        self.active = True
        self.wireless_delay = wireless_delay
        self.power = 0
        self.min_power = 0
        
        # Satelite coordinates
        self.coordinates = coordinates
        
        # Satelite models
        self.mobility_model = None
        self.mobility_model_parameters = {}
        
        self.power_generation_model = None
        self.power_generation_model_parameters = {}
        
        self.power_consumption_model = None
        self.power_consumption_model_parameters = {}
        
        self.failure_model = None
        self.failure_model_parameters = {}
        
            
    def export(self):
        return {
            "id" : self.id,
            "coordinates" : self.coordinates,
            "active" : self.active,
            "power" : self.power,
            "min_power" : self.min_power,
            "wireless_delay" : self.wireless_delay,
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
                "links" : [
                    {
                        "id" : link["id"],
                        "class" : type(link).__name__
                    } for link in self.links
                ],
                
            }
        }
