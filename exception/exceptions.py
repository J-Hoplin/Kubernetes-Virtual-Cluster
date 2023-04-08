class DirectoryNotFound(Exception):
    def __init__(self, directoryName):
        super().__init__(f"Directory '{directoryName}' not found")

class KubectlMayNotInstalled(Exception):
    def __init__(self):
        super().__init__(f"'~/.kube' directory not found. You need to install kubectl fisrt.")
class IllegalControlException(Exception):
    def __init__(self, illegalcontent = None):
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