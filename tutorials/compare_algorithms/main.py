from galeos import*
from tutorials.compare_algorithms.plot import*

import os

from sys import argv

CURRENT_PATH = "tutorials/compare_algorithms"


def stopping_criterion(model) -> bool:
    return model.scheduler.steps == 30


def main():
    algorithms = [
        random_allocation, 
        simple_allocation, 
        best_fit_allocation,
        less_distance_allocation,
        best_exposure_time
    ]
    


    for algorithm in algorithms:
        os.makedirs(os.path.join(CURRENT_PATH, algorithm.__name__ ), exist_ok=True)

        print(algorithm.__name__)

        sim = Simulator(
            stopping_criterion=stopping_criterion,
            resource_management_algorithm=algorithm,
            topology_management_algorithm=default_topology_management,
            ignore_list=[ 
                NetworkFlow, 
                DynamicDurationAccessModel, 
                FixedDurationAccessModel,
                NetworkLink,
                GroundStation,
                ],
            clean_data_in_memory=True,
            logs_directory= os.path.join(CURRENT_PATH, algorithm.__name__ )
        )
    
        sim.initialize("datasets/sample_dataset2.json")

    
    
        sim.run()


    compare_algorithms(*[alg.__name__ for alg in algorithms], current_path=CURRENT_PATH)
     

main()