from galeos import*
import math

def my_algorithm(model, parameters):
    print("Step - ",model.scheduler.steps)
    for app in Application.all():
        if not app.available:  
            process_units = [ unit for unit in ProcessUnit.all() if unit.has_capacity_to_host(app) and unit.available]
            
            if process_units == []:
                continue
            
            key = lambda unit: math.sqrt((unit.cpu - unit.cpu_demand) * (unit.memory - unit.memory_demand) * (unit.storage -unit.storage_demand))
            
            target = min(process_units, key=key)
            
            if target != app.process_unit:
                app.provision(target)
         
         
def stopping_criterion(model) -> bool:
    return model.scheduler.steps == 50


def main():
    sim = Simulator(
        stopping_criterion=stopping_criterion,
        resource_management_algorithm=my_algorithm
    )
    
    sim.initialize('datasets/rnp.json')
    sim.run()
    
    provisioned_time = 0
    non_provisioned_time = 0
    connected_time = 0
    non_connected_time = 0
    
    for user in User.all():
        access_model = user.applications_access_models[0]
        
        for access in access_model.history:
            connected_time += access['access_time']
            provisioned_time += access['provisioned_time']
            non_provisioned_time += access['waiting_provisioning']
            non_connected_time += access['connection_failure_time']
    
    print("Total provisioned time: ", provisioned_time)
    print("Total waiting time: ", non_provisioned_time)
    print("Total connected time: ", connected_time)
    print("Total non connected time: ", non_connected_time)
        
    
main()