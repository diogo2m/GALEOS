from galeos import*

from prometheus_client import Gauge, start_http_server

from tutorials.customizing_galeos.helper_methods import*

load_extensions()

start_http_server(9000)

set_buckets()

def best_fit(app):
    process_units = [ unit for unit in ProcessUnit.all() if unit.has_capacity_to_host(app) and unit.available]
            
    if process_units == []:
        return
            
    key = lambda unit: math.sqrt((unit.cpu - unit.cpu_demand) * (unit.memory - unit.memory_demand) * (unit.storage -unit.storage_demand))
            
    target = min(process_units, key=key)
            
    if target != app.process_unit:
        print(f"Provisionando {app} em {target}")
        app.provision(target)

def my_algorithm(model, parameters):
    
    print(model.scheduler.steps)
    for user in User.all():
        for access_model in user.applications_access_models:
            last_access = access_model.history[-1]

            if last_access['making_request'].get(str(model.scheduler.steps + 1), False):
                best_fit(access_model.application)
            elif access_model.application.available: 
                access_model.application.deprovision()
            

    import time
    time.sleep(1)

def stopping_criterion(model) -> bool:
    return model.scheduler.steps == 10

def main():
    sim = Simulator(
        stopping_criterion=stopping_criterion,
        resource_management_algorithm=my_algorithm,
        topology_management_algorithm=default_topology_management,
        ignore_list=[Application, NetworkFlow, DynamicDurationAccessModel, FixedDurationAccessModel]
    )

    sim.initialize("datasets/rnp.json")

    sim.run()

    for app in Application.all():
        print(app, app.migrations)

main()