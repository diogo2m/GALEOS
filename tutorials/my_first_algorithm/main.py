from galeos import*
from tutorials.my_first_algorithm.plot import*
# from tutorials.customizing_galeos.main import*



def min_delay(user : User, app : Application, current_delay : float = float('inf')) -> bool:
    topology = ComponentManager.model.topology
    process_units = []
    
    
    for access_point in user.network_access_points:
        if isinstance(access_point, Satellite) and access_point.process_unit is not None:
            if access_point.process_unit.has_capacity_to_host(app) and access_point.process_unit.available:
                process_units.append((access_point.wireless_delay, (access_point.process_unit)))
    
    if process_units == []:

        for process_unit in ProcessUnit.all():
            if (process_unit.has_capacity_to_host(app) and process_unit.available) or process_unit == app.process_unit:
                paths = []
                for access_point in user.network_access_points: 
                    if nx.has_path(G=topology, source=access_point, target=process_unit):
                        path = nx.shortest_path(
                            G=topology,
                            source=access_point,
                            target=process_unit,
                            weight='delay'
                        )

                        paths.append(
                            [topology.get_path_delay(path) + path[0].wireless_delay, path]
                        )
                
                if not paths:
                    continue

    
                delay, path = min(paths, key=lambda x: x[0])
                

                process_units.append((delay, process_unit))
            
    if process_units == []:
        print(f"Não há processamento disponível para {app}")

        return False
          
            
    delay, target = min(process_units, key=lambda x: x[0])
            
    current_delay = next((x[0] for x in process_units if x[1] == app.process_unit), float('inf'))
    if target != app.process_unit and current_delay > delay:
        
        print(f"Provisionando {app} em {target}")
        app.provision(target)
        return True
    
    return True


def my_algorithm(model, parameters):
    plot_topology(model.topology, model.scheduler.steps)

    for app in Application.all():
        if app.process_unit and not app.process_unit.available:
            print(f"Deprovisionando {app} de {app.process_unit}")
            app.deprovision()


    # Componentes podem ser manipulados atráves de metodos como all(), count()...
    for user in User.all():
        # Componentes da rede aos quais o usuario pode se conectar
        print(f'The {user} is within range of:', user.network_access_points)

        # Cada usuário pode estar vinculado a varias aplicacoes e esses relacionamentos sao gerenciados atraves de modelos de acesso.
        # Cada classe de modelo de acesso possui caracteristicas especificas que modelam como o usuario pode requisitar uma aplicação
        for access_model in user.applications_access_models:
            print(f'request_provisioning: {access_model.request_provisioning}\tApplication: {access_model.application}')

            # Provisiona se requisitar provisionamento e já não estiver instanciado
            if access_model.request_provisioning and not access_model.application.available:
                min_delay(user,access_model.application)

            # Analisa se será necessário migrar a application
            elif access_model.request_provisioning and access_model.application.available:
                flow = access_model.flow    # Fluxo de dados entre user e application
                
                delay = float('inf')
                if flow and flow.status != 'waiting':  
                    # Calcula o delay para checar se esta dentro do acordado
                    delay = model.topology.get_path_delay(flow.path)
                    delay += flow.path[0].wireless_delay
                    
                    print(f"Path: {flow.path} \tDelay: {delay}")

                
                if delay >= 15:
                    provisioning =  min_delay(user, access_model.application, current_delay=delay)
                    if not provisioning:
                        print(access_model.application.process_unit)
                        access_model.application.deprovision()
                
                
            # Se a applicacao nao estiver sendo requisitada e estiver instanciada 
            elif access_model.application.available: 
                access_model.application.deprovision()



def stopping_criterion(model) -> bool:
    return model.scheduler.steps == 15

def plot_topology(topology, step):
    G = nx.Graph(incoming_graph_data=topology)

    for user in User.all():
        G.add_node(user)

    pos = {}
    colors = []

    for node in GroundStation.all() + User.all() + Satellite.all():

        if hasattr(node, "coordinates") and node.coordinates and len(node.coordinates) >= 2:
            pos[node] = (node.coordinates[1], node.coordinates[0])  

            if isinstance(node, GroundStation):
                c = 'red'
                
            elif isinstance(node, ProcessUnit):
                c = 'blue'  
            elif isinstance(node,Satellite):
                if node.process_unit:
                    c = 'purple'
                else:
                    c = 'green'
            else:
                c = 'yellow'
            
            colors.append(c)
        else:
            # Se não tiver posição, ignora esse nó na visualização
            # print(f"Aviso: Nó {node} não possui coordenadas válidas e será ignorado no plot.")
            pass
    
    # Remover nós sem posição
    nodes_with_pos = list(pos.keys())
    subgraph = G.subgraph(nodes_with_pos)

    plt.figure(figsize=(16, 10),dpi=500)
    nx.draw(
        subgraph,
        pos=pos,
        with_labels=True,
        node_color=[colors[nodes_with_pos.index(n)] for n in subgraph.nodes()],
        node_size=10,
        font_color='black',
        edge_color='gray',
        font_size=3,
        
    )
    plt.title("Visualização do Grafo")
    plt.savefig(f'tutorials/my_first_algorithm/topology/{step}.png')
    plt.close()

def main():

    os.makedirs('tutorials/my_first_algorithm/topology', exist_ok=True)
    
    sim = Simulator(
        stopping_criterion=stopping_criterion,
        resource_management_algorithm=my_algorithm,
        topology_management_algorithm=default_topology_management,
        ignore_list=[ 
            NetworkFlow, 
            DynamicDurationAccessModel, 
            FixedDurationAccessModel,
            NetworkLink,
            GroundStation,
            ],
        clean_data_in_memory=True,
        logs_directory='tutorials/my_first_algorithm/logs',
        dump_interval=20
    )

    
    sim.initialize("datasets/sample_dataset5.json")
    
    
    sim.run()

    # plot_metrics('tutorials/my_first_algorithm/logs/User.jsonl', 'tutorials/my_first_algorithm/')

    with open('tutorials/my_first_algorithm/logs/Application.jsonl', 'r') as file:
        for line in file:
            data = json.loads(line)
            step = data['Step']
            metrics = data['metrics']

            for app in metrics:
                if app['Last Migration'] != None and app['Last Migration']['origin'] != 'None':
                    print(f"App {app['ID']} migrated at step {step} to {app['Last Migration']}")
                    

main()