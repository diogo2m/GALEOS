from ..component_manager import ComponentManager

class NetworkLink(ComponentManager, dict):
    """ 
    Because edges are stored in the form of dictionaries in NetworkX, we maintained a similar
    approach by making the Network Link class inherit from the dict class.
    """
    
    _instances = []
    _object_count = 0
    
    
    default_bandwidth = 100_000 # MB/s 
    default_delay = 1
    
    def __init__(
            self,
            id : int = 0
        ):
        
        self.__class__._instances.append(self)
        self.__class__._object_count += 1
        
        if id == 0: 
            id = self.__class__._object_count
        self["id"] = id

        self["topology"] = None

        self["nodes"] = []

        self["delay"] = 0

        self["bandwidth"] = 0
        
        self["flows"] = []
        
        self["active"] = True
        self['type'] = 'default'
        
    
    def collect_metrics(self) -> dict:
        metrics = {
            "ID" : self['id'],
            "Nodes" : [str(node) for node in self['nodes']],
            "Delay" : self['delay'],
            "Active" : self['active'],
            "Bandwidth" : self['bandwidth'],
            "Type" : self['type']
        }
        
        return metrics  
    
        
    def export(self) -> dict: 
        """ Method that generates a representation of the object in dictionary format to save current context
        """ 
        component = {
            "id" : self['id'],
            "delay" : self['delay'],
            'active' : self['active'],
            'bandwidth' : self['bandwidth'],
            'type' : self['type'],
            'relationships' : {
                "topology": {"class": type(self.topology).__name__, "id": self.topology.id},
                "flows" : [ {"class" : type(flow).__class__, "id" : flow.id} for flow in self['flows']],
                "nodes": [{"class": type(node).__name__, "id": node.id} for node in self.nodes]
            }
        }
        
        return component 
        
        
    def __getattr__(self, attribute_name: str):  
        if attribute_name in self:
            return self[attribute_name]
        else:
            raise AttributeError(f"Object {self} has no such attribute '{attribute_name}'.")


    def __setattr__(self, attribute_name: str, value: object):
        self[attribute_name] = value