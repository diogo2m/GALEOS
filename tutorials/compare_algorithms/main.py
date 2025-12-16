from galeos import *
from tutorials.compare_algorithms.plot import compare_algorithms_averaged # Função nova no plot.py
import tutorials.compare_algorithms.dataset as ds # Importa o arquivo dataset acima

import os
import random
import shutil

CURRENT_PATH = "tutorials/compare_algorithms"
DATASETS_DIR = "datasets"

def clear_all_components():
    # Itera sobre todas as subclasses de ComponentManager e limpa suas instâncias
    for cls in ComponentManager.__subclasses__():
        if cls.__name__ != "Simulator": 
            cls.clear()

def stopping_criterion(model) -> bool:
    return model.scheduler.steps == 100

def main():
    # Configurações
    NUM_REPETITIONS = 10  # Defina o número de repetições
    NUM_USERS = 50
    SCENARIOS = ['terrestrial', 'leo', 'hybrid']
    
    algorithms = [
        random_allocation, 
        simple_allocation, 
        best_fit_allocation,
        less_distance_allocation,
        best_exposure_time
    ]

    # Cria diretório de datasets
    os.makedirs(DATASETS_DIR, exist_ok=True)

    # 1. Loop de Repetições
    for rep in range(1, NUM_REPETITIONS + 1):
        print(f"\n--- Repetição {rep}/{NUM_REPETITIONS} ---")
        
        current_seed = rep 

        total_resources = 0 

        # 2. Gerar os 3 Datasets (Terrestre, LEO, Híbrido)
        datasets_files = {}

        for scenario in SCENARIOS:
            print(f"  Gerando Dataset: {scenario}")
            
            # Limpa memória antes de começar
            clear_all_components()
            
            # RESET
            random.seed(current_seed)
            
            # Carrega Topologia e Usuários
            t = ds.load_topology('datasets/rnp.gml', 'datasets/satellites_brazil.json')
            ds.create_users(NUM_USERS)
            
            # Define total de recursos se ainda não definido (metade dos satélites)
            if total_resources == 0:
                total_resources = Satellite.count() // 2

            # Adiciona Recursos Específicos do Cenário
            if scenario == 'terrestrial':
                ds.add_process_unit_to_ground_stations(t, num_process_units=total_resources)
            
            elif scenario == 'leo':
                ds.add_process_unit_to_satellites(t, num_process_units=total_resources)
            
            elif scenario == 'hybrid':
                half = total_resources // 2
                ds.add_process_unit_to_ground_stations(t, num_process_units=half)
                ds.add_process_unit_to_satellites(t, num_process_units=total_resources - half)
            
            # Configura mobilidade 
            ds.configure_mobility_models()
            
            # Salva o arquivo JSON
            filename = os.path.join(DATASETS_DIR, f"dataset_rep{rep}_{scenario}.json")
            ComponentManager.save_scenary(filename=filename)
            datasets_files[scenario] = filename

        # 3. Executar Simulações para esta Repetição
        for scenario, dataset_path in datasets_files.items():
            print(f"  Executando Cenário: {scenario}")
            
            for algorithm in algorithms:
                algo_name = algorithm.__name__
                print(f"  Executando Algoritmo: {algo_name}")
                
                log_dir = os.path.join(CURRENT_PATH, algo_name, scenario, f"rep{rep}")
                
                if os.path.exists(log_dir):
                    shutil.rmtree(log_dir)
                os.makedirs(log_dir, exist_ok=True)
                
                # Instancia simulador
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
                    logs_directory=log_dir
                )
                
                # Inicializa e roda
                sim.initialize(dataset_path)
                sim.run()

    # 4. Plotagem das Médias
    print("\nGerando Gráficos Comparativos...")
    compare_algorithms_averaged(
        [alg.__name__ for alg in algorithms],
        scenarios=SCENARIOS,
        num_repetitions=NUM_REPETITIONS,
        current_path=CURRENT_PATH
    )

if __name__ == "__main__":
    main()