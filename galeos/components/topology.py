from ..component_manager import ComponentManager
from .network_flow import NetworkFlow
from .network_link import NetworkLink
from .process_unit import ProcessUnit
from .satellite import Satellite

from geopy.distance import geodesic
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
        self.remove_invalid_connections()
        
        
    def reroute_flows(self):
        """ Method that performs the routing of flows whose paths are now invalid
        """
        for flow in NetworkFlow.all():
            path = flow.path

            need_to_reroute = False

            for i in range(len(path)-1):
                link = self[path[i]][path[i+1]]

                if link not in NetworkLink.all():
                    need_to_reroute = True
                    break
                
            if need_to_reroute:

                if nx.has_path(G=self, source=path[0], target=path[-1]):
                    path  = nx.shortest_path(
                        G=self,
                        source=path[0],
                        target=path[-1],
                        weight='delay'
                    )

                else:
                    path = []

                flow.last_path = flow.path 

                flow.path = path 

                for i in range(len(flow.last_path-1)):
                    link = self[flow.last_path[i]].get(flow.last_path[i+1])

                    if link is None:
                        continue
                    link['flows'].remove(flow)

                flow.bandwidth = {}

                for i in range(len(path)):
                    link = self[flow.path[i]][flow.path[i+1]]

                    link['flows'].append(flow)
                    flow.bandwidth[link] = 0
                    
                    
    def remove_invalid_connections(self):
        """ method that reevaluates the existence of links, removing them if they are at a 
        greater distance than supported
        """
        for satellite in Satellite.all():
            for neighbor in self[satellite].neighbors:
                link = self[satellite][neighbor]

                if not isinstance(neighbor, ProcessUnit) and Topology.within_range(satellite, neighbor):
                    NetworkLink.remove(link)

                    self.remove_edge(satellite, neighbor)

                    del self._adj[satellite][neighbor]
                    del self._adj[neighbor][satellite]
                    
    
    @staticmethod               
    def within_range(object_1 : object, object_2 : object):
        """ Method that evaluates whether the distance between two components is within the communication range.
            TODO : Need to develop verification to differentiate the range of different types of links
        """
        distance_nodes = [object_1.max_connection_range, object_2.max_connection_range]
        
        return min(distance_nodes) > geodesic(object_1.coordinates, object_2.coordinates).kilometers
        
        