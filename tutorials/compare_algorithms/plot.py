import json
import os
import matplotlib.pyplot as plt

VALUES = ['ProcessUnit_11', 'ProcessUnit_23', 'ProcessUnit_20', 'ProcessUnit_15', 'ProcessUnit_2', 'ProcessUnit_3', 'ProcessUnit_27', 'ProcessUnit_8', 'ProcessUnit_22', 'ProcessUnit_24', 'ProcessUnit_10', 'ProcessUnit_26', 'ProcessUnit_13', 'ProcessUnit_16', 'ProcessUnit_28', 'ProcessUnit_12', 'ProcessUnit_21', 'ProcessUnit_14', 'ProcessUnit_17', 'ProcessUnit_9', 'ProcessUnit_6', 'ProcessUnit_7', 'ProcessUnit_1', 'ProcessUnit_19', 'ProcessUnit_5', 'ProcessUnit_4', 'ProcessUnit_18', 'ProcessUnit_25']

def compare_algorithms(*algorithm_names, current_path):
    markers = ['o', 'x', 's', '^', 'D', '*', 'v', '+']

    algorithm_steps = {}
    algorithm_provisioned = {}
    algorithm_total_delay = {}
    total_provisioned_counts = {}
    algorithm_not_provisioned = {}
    p = {}


    for algo in algorithm_names:
        algo_path = os.path.join(current_path, algo, 'User.jsonl')  
        steps = []
        provisioned = []
        total_delay = []
        total_not_provisioned = []

        if not os.path.isfile(algo_path):
            print(f"Warning: File not found for {algo} at {algo_path}")
            continue

        with open(algo_path, 'r') as file:
            last_accesses = {}
            current_access = {}
            waiting = {}
            for line in file:
                data = json.loads(line)
                step = data['Step']
                step_provisioned = 0
                delay_prov = 0
                not_provisioned = 0
                

                for metric in data['metrics']:
                    current_access = metric['Access to Applications'][0] # Assuming only one application per user

                    if last_accesses.get(metric['ID']) is None:
                        last_accesses[metric['ID']] = current_access
                        waiting[metric['ID']] = []
                        continue
                    
                    last_access = last_accesses[metric['ID']]
                    # if last_access['Request Provisioning'] and ( current_access['Provisioning'] == False):
                    if last_access['Request Provisioning'] and ( not current_access['Is Provisioned']):
                        not_provisioned += 1
                        
                        waiting[metric['ID']].append(step)
                    # if current_access['Provisioning']:
                    if current_access['Is Provisioned'] or current_access['Provisioning'] == False:
                        step_provisioned += 1
                        delay_prov += current_access['Delay'] if current_access['Delay'] != float('inf') else 0
                    last_accesses[metric['ID']] = current_access

                steps.append(step)
                provisioned.append(step_provisioned)
                total_delay.append(delay_prov)
                total_not_provisioned.append(not_provisioned)


        count = 0

        for id in waiting:
            for i in range(len(waiting[id])-1):
                if waiting[id][i+1] - waiting[id][i] > 1:
                    count += 1

        p[algo] = count

        print(f'{algo} \t\t=> {sum(provisioned)}')

        
                   
        algorithm_steps[algo] = steps
        algorithm_provisioned[algo] = provisioned
        algorithm_total_delay[algo] = total_delay
        algorithm_not_provisioned[algo] = total_not_provisioned
        total_provisioned_counts[algo] = sum(provisioned)


    # print([ p[algo] for algo in algorithm_not_provisioned])
    # Plot 1: Number of provisioned application
    plt.figure(figsize=(12, 7))
    for i, algo in enumerate(algorithm_names):
        if algo in algorithm_steps:
            plt.plot(algorithm_steps[algo], algorithm_provisioned[algo], label=algo, marker=markers[i % len(markers)])
    plt.xlabel('Step')
    plt.ylabel('Number of Provisioned Applications')
    plt.title('Provisioned Applications per Algorithm')
    plt.grid(True)
    plt.legend()
    plt.savefig("tutorials/compare_algorithms/provisioned.png")

    # Plot 2: Total delay
    plt.figure(figsize=(12, 7))
    for i, algo in enumerate(algorithm_names):
        if algo in algorithm_steps:
            plt.plot(algorithm_steps[algo], algorithm_total_delay[algo], label=algo, marker=markers[i % len(markers)])
    plt.xlabel('Step')
    plt.ylabel('Total Delay')
    plt.title('Total Provisioning Delay per Algorithm')
    plt.grid(True)
    plt.legend()
    plt.savefig('tutorials/compare_algorithms/delay.png')

    # Plot 2: Applications not provisioned
    plt.figure(figsize=(12, 7))
    for i, algo in enumerate(algorithm_names):
        if algo in algorithm_steps:
            plt.plot(algorithm_steps[algo], algorithm_not_provisioned[algo], label=algo, marker=markers[i % len(markers)])
    plt.xlabel('Step')
    plt.ylabel('Applications Not Provisioned')
    plt.title('Total Not Provisioned Applications per Algorithm')
    plt.grid(True)
    plt.legend()
    plt.savefig('tutorials/compare_algorithms/not_provisioned.png')

    # Get total migrations and generate bar chart
    total_migrations_counts, algorithm_migr = plot_migrations(*(algorithm_names), current_path=current_path)

    # Plot 3: Total provisioned and migrations (bar plot)
    plt.figure(figsize=(10, 6))
    x = range(len(algorithm_names))
    provision_vals = [total_provisioned_counts.get(algo, 0) for algo in algorithm_names]
    migration_vals = [total_migrations_counts.get(algo, 0) for algo in algorithm_names]

    bar_width = 0.35
    plt.bar(x, provision_vals, width=bar_width, label='Total Provisioned', color='skyblue')
    plt.bar([p + bar_width for p in x], migration_vals, width=bar_width, label='Total Migrations', color='salmon')

    plt.xticks([p + bar_width / 2 for p in x], algorithm_names)
    plt.ylabel('Count')
    plt.title('Total Provisioned vs Migrations per Algorithm')
    plt.legend()
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("tutorials/compare_algorithms/total_bar_chart.png")


def plot_migrations(*algorithm_names, current_path):
    algorithm_steps = {}
    algorithm_migrations = {}
    total_migrations_counts = {}

    for algo in algorithm_names:
        algo_path = os.path.join(current_path, algo, 'Application.jsonl')  
        steps = []
        migrations = []
        allocations_in_ground_infraestructure = 0
        allocations_in_air_infraestructure = 0 

        if not os.path.isfile(algo_path):
            print(f"Warning: File not found for {algo} at {algo_path}")
            continue

        with open(algo_path, 'r') as file:
            x = 0
            for line in file:
                data = json.loads(line)
                step = data['Step']
                current_migrations = 0 + x

                for metric in data['metrics']:
                    migr = metric.get('Last Migration')
                    if migr and migr.get('start') == step :
                        current_migrations += 1

                    if migr and migr.get('start') == step and migr['target'] in VALUES:
                        allocations_in_ground_infraestructure += 1
                    elif migr and migr.get('start') == step and migr['target'] not in VALUES:
                        allocations_in_air_infraestructure += 1
                
                x = current_migrations

                steps.append(step)
                migrations.append(current_migrations)

        algorithm_steps[algo] = steps
        algorithm_migrations[algo] = migrations
        total_migrations_counts[algo] = sum(migrations)

        print(f'{algo} \t\t=> Terrestre: {allocations_in_ground_infraestructure}\tLEO: {allocations_in_air_infraestructure}')

    # Plot: Migrations per step
    plt.figure(figsize=(12, 7))
    for i, algo in enumerate(algorithm_names):
        if algo in algorithm_steps:
            plt.plot(algorithm_steps[algo], algorithm_migrations[algo], label=algo, marker='x')
    plt.xlabel('Step')
    plt.ylabel('Number of Migrations')
    plt.title('Migrations per Algorithm')
    plt.grid(True)
    plt.legend()
    plt.savefig("tutorials/compare_algorithms/migrations.png")

    return total_migrations_counts, algorithm_migrations
