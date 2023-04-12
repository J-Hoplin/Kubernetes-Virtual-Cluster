from utils.utility import Utility
from exception import exceptions

class InstanceExistChecker(Utility):

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, fn):
        def wrapper(instance,name, *args, **kwargs):
            workerNodeName = self.getNodeName(name)
            if self.checkInstanceNameNotInUse(workerNodeName):
                raise exceptions.NodeNotFound(workerNodeName)
            result = fn(instance,name,node_name=workerNodeName)
            return result
        return wrapper