from utils.utility import Utility
from exception import exceptions


class InstanceNameAlreadyTakenChecker(Utility):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, fn):
        def wrapper(instance, name, *args, **kwargs):
            # Check instance name in use
            if not self.checkInstanceNameNotInUse(name):
                raise exceptions.InvalidNodeGenerationDetected(
                    self.getCriticalMessage(
                        f"Name with '{name}' already in use! Ignore generating worker-node config '{name}'"))
            result = fn(instance, name, args, node_name=name)
            return result
        return wrapper
