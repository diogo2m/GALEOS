from ...components import*


class DefaultScheduler:
    """ Class responsible for scaling simulator components
    """
    def __init__(self, model : object):
        self.model = model
        self.steps = 0
    
    def step(self):
        """ Method that performs the scheduling of components in standard order
        """
        
        self.model.resource_management_algorithm(self.model.resource_management_parameters)

        for satellite in Satellite.all():
            satellite.step()
        
        for ground_station in GroundStation.all():
            ground_station.step()
            
        self.topology.step()
        
        for user in User.all():
            user.step()
            
        for process_unit in ProcessUnit.all():
            process_unit.step()
        
        for application in Application.all():
            application.step()
            
        self.steps += 1