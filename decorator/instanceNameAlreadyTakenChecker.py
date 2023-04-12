from utils.utility import Utility
from exception import exceptions

class InstanceNameAlreadyTakenChecker(Utility):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self,fn):
        def wrapper(instance,name,*args,**kwargs):
            workerNodeName = self.getNodeName(name)
            # Check instance name in use
            if not self.checkInstanceNameNotInUse(workerNodeName):
                raise exceptions.InvalidNodeGenerationDetected(
                    self.getCriticalMessage(
                        f"Name with '{workerNodeName}' already in use! Ignore generating worker-node config '{name}'"))
            result = fn(instance,name,node_name=workerNodeName)
            return result
        return wrapper
