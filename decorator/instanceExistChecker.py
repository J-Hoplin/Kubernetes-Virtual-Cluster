from utils.utility import Utility
from exception import exceptions


class InstanceExistChecker(Utility):

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, fn):
        def wrapper(instance, name, *args, **kwargs):
            if self.checkInstanceNameNotInUse(name):
                raise exceptions.NodeNotFound(name)
            result = fn(instance, name, node_name=name)
            return result
        return wrapper
