from ..ground_station import GroundStation
from ..satellite import Satellite
from ..network_link import NetworkLink
from ..network_flow import NetworkFlow
from ..process_unit import ProcessUnit

from geopy.distance import geodesic
import numpy as np
import networkx as nx


def barabasi_albert(topology, min_num_links : int = 2):

    satellites = Satellite.all()

    for satellite in satellites:
        targets = [
            neighbor for neighbor in satellites 
            if neighbor != satellite and neighbor not in topology[satellite] and topology.within_range(satellite, neighbor)
        ]
    
        
        for target in targets:
            link = NetworkLink(satellite, target)
            
            topology.add_edge(satellite, target, link=link)
            
            topology._adj[satellite][target]
            topology._adj[target][satellite]




def default_topology_management(topology : object, **parameters):
    
    topology.remove_invalid_connections()
    
    barabasi_albert(
        topology=topology, 
        min_num_links=parameters.get('min_num_links', 2)
    )
    
    topology.reroute_flows()
    
    
    
    
                
