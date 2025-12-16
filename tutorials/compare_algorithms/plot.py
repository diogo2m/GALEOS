import json
import os
import matplotlib.pyplot as plt

# Função principal de comparação com suporte a médias
def compare_algorithms_averaged(algorithm_names, scenarios, num_repetitions, current_path):
    markers = ['o', 'x', 's', '^', 'D', '*', 'v', '+']

    # Gera um conjunto de gráficos para CADA cenário
    for scenario in scenarios:
        print(f"Processando gráficos para o cenário: {scenario}")
        
        # Dicionários para guardar os dados médios de cada algoritmo
        # Formato: algo_name -> [valor_step_0, valor_step_1, ...]
        avg_steps = {} 
        avg_provisioned = {}
        avg_delay = {}
        avg_not_provisioned = {}
        
        for algo in algorithm_names:
            # Listas temporárias para acumular dados de todas as repetições
            # ex: reps_provisioned = [ [prov_rep1_step0, ...], [prov_rep2_step0, ...] ]
            reps_provisioned = []
            reps_delay = []
            reps_not_provisioned = []
            
            captured_steps = [] # Para guardar o eixo X
            
            for rep in range(1, num_repetitions + 1):
                # Caminho: Algo / Scenario / repX / User.jsonl
                file_path = os.path.join(current_path, algo, scenario, f"rep{rep}", 'User.jsonl')
                
                if not os.path.isfile(file_path):
                    print(f"  AVISO: Arquivo não encontrado: {file_path}")
                    continue
                
                # Leitura do arquivo (lógica original adaptada)
                curr_steps = []
                curr_prov = []
                curr_delay = []
                curr_not_prov = []
                
                with open(file_path, 'r') as file:
                    last_accesses = {}
                    for line in file:
                        data = json.loads(line)
                        step = data['Step']
                        
                        step_provisioned = 0
                        delay_prov = 0
                        not_provisioned = 0
                        
                        for metric in data['metrics']:
                            current_access = metric['Access to Applications'][0]

                            if last_accesses.get(metric['ID']) is None:
                                last_accesses[metric['ID']] = current_access
                                continue
                            
                            last_access = last_accesses[metric['ID']]
                            
                            if last_access['Request Provisioning'] and (not current_access['Is Provisioned']):
                                not_provisioned += 1
                                
                            if current_access['Is Provisioned'] or current_access['Provisioning'] == False:
                                step_provisioned += 1
                                delay_prov += current_access['Delay'] if current_access['Delay'] != float('inf') else 0
                            
                            last_accesses[metric['ID']] = current_access
                        
                        curr_steps.append(step)
                        curr_prov.append(step_provisioned)
                        curr_delay.append(delay_prov)
                        curr_not_prov.append(not_provisioned)

                reps_provisioned.append(curr_prov)
                reps_delay.append(curr_delay)
                reps_not_provisioned.append(curr_not_prov)
                
                if not captured_steps:
                    captured_steps = curr_steps
            
            # Calcular Médias (se houver dados)
            if reps_provisioned:
                # Determina o tamanho mínimo (caso alguma simulação tenha parado antes)
                min_len = min(len(r) for r in reps_provisioned)
                
                # Função auxiliar para média de lista de listas
                def calc_avg(list_of_lists, length):
                    result = []
                    for i in range(length):
                        soma = sum(l[i] for l in list_of_lists)
                        result.append(soma / len(list_of_lists))
                    return result
                
                avg_steps[algo] = captured_steps[:min_len]
                avg_provisioned[algo] = calc_avg(reps_provisioned, min_len)
                avg_delay[algo] = calc_avg(reps_delay, min_len)
                avg_not_provisioned[algo] = calc_avg(reps_not_provisioned, min_len)

        # --- Plotagem ---
        
        # 1. Provisioned Applications
        plt.figure(figsize=(12, 7))
        for i, algo in enumerate(algorithm_names):
            if algo in avg_provisioned:
                plt.plot(avg_steps[algo], avg_provisioned[algo], label=algo, marker=markers[i % len(markers)])
        plt.xlabel('Step')
        plt.ylabel('Avg Number of Provisioned Applications')
        plt.title(f'Provisioned Applications - {scenario.capitalize()}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(current_path, f"provisioned_{scenario}.png"))
        plt.close()

        # 2. Total Delay
        plt.figure(figsize=(12, 7))
        for i, algo in enumerate(algorithm_names):
            if algo in avg_delay:
                plt.plot(avg_steps[algo], avg_delay[algo], label=algo, marker=markers[i % len(markers)])
        plt.xlabel('Step')
        plt.ylabel('Avg Total Delay')
        plt.title(f'Total Provisioning Delay - {scenario.capitalize()}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(current_path, f"delay_{scenario}.png"))
        plt.close()

        # 3. Not Provisioned
        plt.figure(figsize=(12, 7))
        for i, algo in enumerate(algorithm_names):
            if algo in avg_not_provisioned:
                plt.plot(avg_steps[algo], avg_not_provisioned[algo], label=algo, marker=markers[i % len(markers)])
        plt.xlabel('Step')
        plt.ylabel('Avg Applications Not Provisioned')
        plt.title(f'Not Provisioned Applications - {scenario.capitalize()}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(current_path, f"not_provisioned_{scenario}.png"))
        plt.close()