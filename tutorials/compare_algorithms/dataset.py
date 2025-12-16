from galeos import *
from dataset_generator import *
from random import seed, randint, sample


def load_topology(ground_topology: str, leo_topology) -> Topology:
    t = load_ground_topology_from_gml(ground_topology)

    create_satellite_topology(
        topology=t,
        filename=leo_topology,
        max_steps=180, 
        sat_range=200,
        max_satellites=10
    )

    for sat in Satellite.all():
        sat.is_gateway = False

    for sat in sample(Satellite.all(), Satellite.count()//2):
        sat.is_gateway = True

    for station in GroundStation.all():
        for sat in Satellite.all():
            if sat.coordinates is None:
                continue
            
            if t.within_range(station, sat) and sat.is_gateway:
                if t.has_edge(station, sat):
                    continue
                create_link(sat, station, topology=t)
    return t

def create_users(num_users: int) -> None:
    # Coleta coordenadas possíveis
    coordinates_history = [coor for sat in Satellite.all() for coor in sat.coordinates_trace if coor is not None]

    for coordinates in sample(coordinates_history, k=num_users):
        user = create_user(coordinates)
        user.mobility_model = random_mobility_model
        
        create_application_to_user(
            user=user,
            cpu_demand=randint(1, 5),
            memory_demand=randint(1, 5),
            access_class=DynamicDurationAccessModel
        )

def add_process_unit_to_satellites(topology, num_process_units: int):
    targets = sample(Satellite.all(), min(num_process_units, Satellite.count()))
    
    for satellite in targets:
        unit = ProcessUnit(
            cpu=randint(15, 20),
            memory=randint(15, 20),
            storage=randint(15, 20)
        )
        unit.coordinates = satellite.coordinates
        create_link(unit, satellite, 1, bandwidth=NetworkLink.default_bandwidth, topology=topology)
        satellite.process_unit = unit

def add_process_unit_to_ground_stations(topology, num_process_units: int):
    targets = sample(GroundStation.all(), min(num_process_units, GroundStation.count()))
    
    for station in targets:
        unit = ProcessUnit(
            cpu=randint(20, 50),
            memory=randint(20, 50),
            storage=randint(20, 50)
        )
        unit.coordinates = station.coordinates
        create_link(unit, station, 10, NetworkLink.default_bandwidth, topology=topology)
        station.process_unit = unit

def configure_mobility_models():
    history = [coor for sat in Satellite.all() for coor in sat.coordinates_trace if coor is not None] 
    
    for sat in Satellite.all():
        sat.coordinates_trace = history
        sat.mobility_model = coordinates_history 
        sat.mobility_model_parameters = {'len': len(sat.coordinates_trace)}