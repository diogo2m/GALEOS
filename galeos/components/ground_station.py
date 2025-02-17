from ..component_manager import ComponentManager
from .satellite import Satellite

from geopy.distance import distance

class GroundStation(ComponentManager):
    _instances = []
    _object_count = 0
    
    def __init__(
            self,
            id : int = 0,
            coordinates : tuple = None,
            wireless_delay : int = 0, 
            connection_range : int = 500
        ):
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            id = self.__class__._object_count
        self.id = id
        
        self.coordinates = coordinates
        
        self.wireless_delay = wireless_delay
        self.connection_range = connection_range
        
        self.links = []
        self.users = []
        
        
    def export(self):
        """ Method that generates a representation of the object in dictionary format to save current context
        """
        return {
            "id" : self.id,
            "coordinates" : self.coordinates,
            "wireless_delay" : self.coordinates,
            "connection_range" : self.connection_range,
            "relationships" : {
                "links" : [
                    {
                        "id" : link['id'],
                        "class" : type(link).__name__
                    } for link in self.links
                ]
            }
        }
    
    
    def step(self):
        """ Method that executes the object's events
        """
        pass
        
    