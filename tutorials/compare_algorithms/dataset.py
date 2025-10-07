from galeos import*
from dataset_generator import*

from random import seed, randint, sample

seed(0)

def get_satellites(point, steps,interval : 15, radius : 50):
    data = []
    point
    i = 0
    while i < steps:
        print(i)

        try:
            d = get_satellites_from_api(point, sat_range=radius)
            data.append(d)

            sleep(interval)
            i+=1
        except:
            pass

    return data


def load_topology(ground_topology : str, leo_topology) -> Topology:
    t = load_ground_topology_from_gml(ground_topology)

    create_satellite_topology(
        topology=t,
        filename=leo_topology,
        max_steps=180, 
        sat_range=200,
        max_satellites=300
    )

    for sat in Satellite.all():
        sat.is_gateway = False

    for sat in sample(Satellite.all(), Satellite.count()//2):
        sat.is_gateway = True

    for station in GroundStation.all():
        for sat in Satellite.all():
            if sat.coordinates is None :
                continue
            
            if t.within_range(station, sat) and sat.is_gateway:
                if t.has_edge(station, sat):
                    continue
                
                create_link(sat, station, topology=t)
    
    return t


def create_users(num_users : int) -> None:
  
    coordinates_history = [coor  for sat in Satellite.all() for coor in sat.coordinates_trace if coor is not None]

    
    for coordinates in sample(coordinates_history, k=num_users):
        user  = create_user(coordinates)
        
        user.mobility_model = random_mobility_model
        
        create_application_to_user(
            user=user,
            cpu_demand=randint(1, 5),
            memory_demand=randint(1, 5),
            access_class=DynamicDurationAccessModel
        )
   
   


def add_process_unit_to_satellites(topology, num_process_units : int = None):
    targets = sample(
        Satellite.all(), 
        min(num_process_units, Satellite.count()) if num_process_units else Satellite.count()
    )
    
    for satellite in targets:
        unit = ProcessUnit(
            cpu=randint(15, 20),
            memory=randint(15,20),
            storage=randint(15,20)
        )

        unit.coordinates = satellite.coordinates
        
        create_link(unit, satellite, 1, bandwidth=NetworkLink.default_bandwidth, topology=topology)
        
        satellite.process_unit = unit


def add_process_unit_to_ground_stations(topology, num_process_units : int = None):
    
    targets = sample(
        GroundStation.all(),
        min(num_process_units, GroundStation.count()) 
    )
    
    for station in targets:
        unit = ProcessUnit(
            cpu=randint(20, 50),
            memory=randint(20,50),
            storage=randint(20, 50)
        )

        unit.coordinates = station.coordinates
        
        create_link(unit, station, 10, NetworkLink.default_bandwidth, topology=topology)
        
def create_dataset(ground_topology : str, leo_topology : str, filename : str):
    t = load_topology(ground_topology, leo_topology)
    
    create_users(20)
    
    # add_process_unit_to_ground_stations(t, num_process_units=GroundStation.count() // 2)
    add_process_unit_to_satellites(t, num_process_units=Satellite.count() // 2)
    
    for sat in  Satellite.all():
        sat.mobility_model = coordinates_history
        sat.mobility_model_parameters = {'len' : len(sat.coordinates_trace)}
    
    ComponentManager.save_scenary(filename=filename)

def main():

    
    create_dataset(
        ground_topology='datasets/rnp.gml',
        leo_topology='satellites2.json',
        filename="datasets/sample_dataset2.json"
    )

            

main()
