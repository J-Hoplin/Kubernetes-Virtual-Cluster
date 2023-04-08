class DirectoryNotFound(Exception):
    def __init__(self, directoryName):
        super().__init__(f"Directory '{directoryName}' not found")


class KubectlMayNotInstalled(Exception):
    def __init__(self):
        super().__init__(f"'~/.kube' directory not found. You need to install kubectl fisrt.")


class IllegalControlException(Exception):
    def __init__(self, illegalcontent=None):
        super().__init__(f"Illegal control detected : {illegalcontent}")


class MasterNodeConfigNotFound(Exception):
    def __init__(self):
        super().__init__("Master node config should define with key name 'master-node' in nodes/master/config.json")


class NoneTypeValueDetected(Exception):
    def __init__(self):
        super().__init__("None type value expected!")


class WrongArgumentGiven(Exception):
    def __init__(self):
        super().__init__("Wrong argument value given")


class ImproperMasterNodeGenerated(Exception):
    def __init__(self):
        statement = """
        Something went wrong while generating Master Node!
        - Please check computer's resource and network!
        
        1. Please delete master node instance using 'python3 cluster.py -c terminate'
        2. Restart Multipass
        """
        super().__init__(statement)

class MasterNodeNotFound(Exception):
    def __init__(self):
        super().__init__("Master node not generated! Please initiate cluster before add worker node")

class RequiredCommandLineOptionLost(Exception):
    def __init__(self, name):
        super().__init__(f"Required option '{name}' lost")

class NodeNotFound(Exception):
    def __init__(self,name):
        super().__init__(f"Node not found : {name}")

class InvalidConfigType(Exception):
    def __init__(self, tp):
        super().__init__(
            f"Invalid config type detected. Should be type '{tp}'")
