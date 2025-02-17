from ..component_manager import ComponentManager
from .ground_station import GroundStation
from .network_link import NetworkLink
from .satellite import Satellite

import networkx as nx


class Topology(ComponentManager, nx.Graph):

    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = 0, existing_graph: nx.Graph = None) -> object:
       
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0:
            obj_id = self.__class__._object_count
        self.id = obj_id

        if existing_graph is None:
            nx.Graph.__init__(self)
        else:
            nx.Graph.__init__(self, incoming_graph_data=existing_graph)
            
        self.satellites = []
            
    def step(self):
        """ Method that executes the object's events
        """
        for satellite in Satellite.all():
            pass