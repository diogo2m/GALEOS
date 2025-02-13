
class DefaultScheduler:
    """ Class responsible for scaling simulator components
    """
    def __init__(self, model : object):
        self.model = model
        self.steps = 0
    
    def step(self):
        """ Method that performs the scheduling of components in standard order
        """
        
        self.steps += 1