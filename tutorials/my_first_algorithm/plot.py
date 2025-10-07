import json
import matplotlib.pyplot as plt

def plot_metrics(file_path, folder_name):
    steps = []
    provisioned = []
    not_provisioned = []
    total_delay_provisioned = []
    total_delay_not_provisioned = []

    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            step = data['Step']
            step_provisioned = 0
            step_not_provisioned = 0
            delay_prov = 0
            delay_not_prov = 0

            for metric in data['metrics']:
                for access in metric['Access to Applications']:
                    if access['Request Provisioning'] and access['Provisioning']:
                        step_provisioned += 1
                        delay_prov += access['Delay'] if access['Delay'] != float('inf') else 0
                    elif access['Request Provisioning']:
                        step_not_provisioned += 1
                        delay_not_prov += access['Delay'] if access['Delay'] != float('inf') else 0

            steps.append(step)
            provisioned.append(step_provisioned)
            not_provisioned.append(step_not_provisioned)
            total_delay_provisioned.append(delay_prov)
            total_delay_not_provisioned.append(delay_not_prov)

    # Plot 1: Provisioned vs Not Provisioned
    plt.figure(figsize=(10, 6))
    plt.plot(steps, provisioned, label='Provisioned', marker='o')
    plt.plot(steps, not_provisioned, label='Not Provisioned', marker='x')
    plt.xlabel('Step')
    plt.ylabel('Number of Services')
    plt.title('Provisioned vs Not Provisioned per Step')
    plt.legend()
    plt.grid(True)
    plt.savefig(folder_name + "/time_x_time.png")
    plt.close()

    # Plot 2: Total Delay 
    plt.figure(figsize=(10, 6))
    plt.plot(steps, total_delay_provisioned, label='Total Delay - Provisioned', marker='o')
    plt.plot(steps, provisioned, label='Provisioned', marker='o')
    plt.xlabel('Step')
    plt.ylabel('Total Delay')
    plt.title('Total Provisioning Delay per Step')
    plt.legend()
    plt.grid(True)
    plt.savefig( folder_name + "/delay_x_applications")
    plt.close()

