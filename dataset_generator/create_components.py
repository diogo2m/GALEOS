from galeos.components import User,Application, CyclicApplicationAccessModel,Topology, NetworkLink, Satellite, mesh_network

from random import choices
import requests
from datetime import datetime
from time import sleep


N2YO_API_KEY = "KTWK48-4U9L6A-4CMGWN-583R"
REFERENCE_POINT = (-15.669171, -48.013922, 0)

def create_user(
        coordinates : tuple,
        connection_range : int = 500
    ) -> User:
    
    user = User(
        coordinates=coordinates,
        max_connection_range=connection_range
    )
        
    user.mobility_model = None
    user.mobility_model_parameters = {}
        
  
def create_application_to_user(
        user : User,
        cpu_demand : int = 0,
        memory_demand : int = 0,
        storage_demand : int = 0,
        state : int = 0,
        sla : int = 0
    ):
    
    app = Application(
        cpu_demand=cpu_demand,
        memory_demand=memory_demand,
        storage_demand=storage_demand,
        state=state,
        sla=sla,
    )
    
    values = [ j for j in range(20)]
    
    access_model = CyclicApplicationAccessModel(
        user=user,
        application=app,
        start=1,
        duration_values=choices(values, k=5),
        interval_values=choices(values, k=5),
        connection_duration_values=choices(values, k=5),
        connection_interval_values=choices(values, k=5)
    )
    
    user.connection_to_application(application=app, access_model=access_model)
        
        
def create_link(
        v1 : object, 
        v2 : object,
        delay : int = 1,
        bandwidth : int = 12,
        topology : object = None
    ):
    
    link = NetworkLink()
    
    link['topology'] = topology
    link['nodes'] = [v1, v2]
    link['bandwidth'] = bandwidth
    link['delay'] = delay
    link['type'] = 'static'
    
    topology.add_edge(v1, v2)
        
    topology._adj[v1][v2] = link
    topology._adj[v2][v1] = link
    
    
   
    
def get_satellites_from_api( coordinates, sat_range, api_category: int = 52) -> dict:
    API_URL = f"https://api.n2yo.com/rest/v1/satellite/above/{coordinates[0]}/{coordinates[1]}/{coordinates[2] if len(coordinates) > 2 else 0}/{sat_range}/{api_category}/&apiKey={N2YO_API_KEY}"
    try:
        response = requests.get(url=API_URL)
    except:
        print("Unable to grab satellites from API")
        return
    
    return response.json()["above"]


def load_satellites(
        max_steps : int = 10,
        interval : int = 30,
        sat_range : int = 1000,
        api_category: int = 52, 
        max_satellites: int = None
    ) -> None:
    """ Function that captures information about satellites around a reference point over a period of time 
    and creates satellites with this information. 
    No computational units are assigned to any of these satellites.

    """
    sats = {}
    
    for i in range(max_steps):
        current_step = get_satellites_from_api(REFERENCE_POINT, sat_range=sat_range, api_category=api_category)
        
        for sat in current_step:
            id = sat['satid']
            coordinates = (sat['satlat'], sat['satlng'], sat['satalt'])
            
            if id in sats:
                satellite = sats[id]
                
                satellite.coordinates_trace.append(coordinates)
                
            elif Satellite.count() < max_satellites:
                satellite = Satellite(
                    name=f"SATELLITE-{id}",
                    coordinates=coordinates,
                    max_connection_range=300
                )
                
                # satellite.mobility_model = coordinates_history
                satellite.coordinates_trace.extend([None for _ in range(i)] + [coordinates])
                
                sats[id] = satellite
                
        sleep(interval)
                

def create_satellite_topology(
        topology : Topology,
        max_steps : int = 10,
        interval : int = 30,
        sat_range : int = 1000,
        max_satellites: int = None
    ):
    
    load_satellites(max_steps,interval, sat_range, max_satellites)
    
    mesh_network(topology)
    
