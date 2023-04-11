import subprocess
import json
import os
from exception import exceptions
from colorama import Fore, Style


class Assets(object):
    MASTER_NODE_KEY = 'master-node'
    MASTER_CONFIG = './nodes/master/config.json'
    WORKER_CONFIG = './nodes/worker/config.json'
    SCRIPT_PATH= './scripts'
    KUBE_CONFIG_DIR = f"{os.environ['HOME']}/.kube"
    KUBE_CONFIG = f"{os.environ['HOME']}/.kube/config"

class NodeType(object):
    MASTER = 'master'
    WORKER = 'worker'


class Resolver(object):
    def __init__(self):
        pass

    def typeChecker(self, obj, tp):
        return type(obj) == tp

    def readConfig(self, file) -> dict:
        with open(file, 'r') as config:
            content: dict = json.load(config)
            return content

    def saveConfig(self, file, object):
        with open(file, 'w') as config:
            json.dump(object, config, indent=4)

    def getNodeName(self,name: str):
        return "-".join(name.lower().split(" "))
    def getCriticalMessage(self,msg):
        return Fore.RED + f"Critical : {msg}" + Style.RESET_ALL

    def getNormalMessage(self,msg):
        return Fore.GREEN + msg + Style.RESET_ALL
    def getWarningMessage(self,msg):
        return Fore.YELLOW + f"Warn : {msg}" + Style.RESET_ALL

    def getSpecialMessage(self,msg):
        return Fore.MAGENTA + msg + Style.RESET_ALL

    def checkInstanceNameNotInUse(self,name) -> bool:
        hit = True
        '''
        Slice 0 index value : 0 index result of command is index of column
        '''
        for i in map(lambda x: x.split(),
                     subprocess.run(["multipass", "list"], stdout=subprocess.PIPE)
                             .stdout.decode('utf-8')
                             .split("\n")[1:]):
            try:
                if i[0] == name:
                    hit = False
                    break
            except:
                continue
        return hit

    def cluster_init(self):
        os.system('clear')

        def NodeInit(name, cpu, memory, disk, tp, *args):
            if tp == NodeType.MASTER:
                subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", name,
                               cpu, memory, disk, tp], stdout=subprocess.PIPE)
            elif tp == NodeType.WORKER:
                token, ip = args
                subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", name, cpu,
                               memory, disk, tp, token, ip], stdout=subprocess.PIPE)
            else:
                raise exceptions.IllegalControlException("Invalid node type")

        def getNodeIP(name):
            return subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/getNodeIP.sh", name], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        if not os.path.exists('./nodes'):
            raise exceptions.DirectoryNotFound('nodes')

        # Get master node config
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)

        print(self.getNormalMessage("Complete to load : Master config"))

        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        print(self.getNormalMessage("Complete to load : Worker config"))

        # Initialize master node config

        if Assets.MASTER_NODE_KEY not in masterConfig:
            raise exceptions.MasterNodeConfigNotFound()

        # Check
        if not self.checkInstanceNameNotInUse(Assets.MASTER_NODE_KEY):
            raise exceptions.InvalidNodeGenerationDetected(
                self.getCriticalMessage(f"Instance with '{Assets.MASTER_NODE_KEY}' already in use! Stop generating cluster.")
            )

        print(self.getNormalMessage(f"Initiating {Assets.MASTER_NODE_KEY} ..."))
        masterNodeName: str = Assets.MASTER_NODE_KEY
        masterNodeInfo: dict = masterConfig[masterNodeName]

        '''
        If invalid config type
        
        Node config type should be dictionary
        
        -> Master Node : Raise Exception
        -> Worker Node : Ignore
        '''
        if not self.typeChecker(masterNodeInfo, dict):
            raise exceptions.InvalidConfigType(dict)

        masterNodeCPU = masterNodeInfo.get(
            'cpu', os.environ['MASTER_DEFAULT_CPU'])
        masterNodeMemory = masterNodeInfo.get(
            'memory', os.environ['MASTER_DEFAULT_MEMORY'])
        masterNodeStorage = masterNodeInfo.get(
            'disk', os.environ['MASTER_DEFAULT_STORAGE'])
        NodeInit(masterNodeName, masterNodeCPU, masterNodeMemory,
                 masterNodeStorage, NodeType.MASTER)

        masterNodeIP = getNodeIP(masterNodeName)
        masterConfig[masterNodeName]["ip"] = masterNodeIP
        masterNodeToken = subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/getMasterToken.sh", masterNodeName], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        masterConfig[masterNodeName]["token"] = masterNodeToken

        if (not masterNodeIP) or (not masterNodeToken):
            raise exceptions.ImproperMasterNodeGenerated()

        print(self.getSpecialMessage(f"Master Node IP : {masterNodeIP}"))
        print(self.getSpecialMessage(f"Master Node Token : {masterNodeToken}"))
        print(self.getNormalMessage("Complete to build master node ..."))

        # Initialize worker node config
        for i, j in workerConfig.items():
            workerNodeName: str = self.getNodeName(i)

            if not self.checkInstanceNameNotInUse(workerNodeName):
                print(self.getCriticalMessage(f"Instance with name '{workerNodeName}' already in use! Ignore generating worker-node config '{i}'"))
                continue

            workerNodeInfo: dict = j

            if not self.typeChecker(workerNodeInfo, dict):
                print(self.getCriticalMessage(f"Invalid config type of worker node : {workerNodeName}!"))
                continue
            print(self.getNormalMessage(f"Initiating worker node : {workerNodeName} ..." ))
            workerNodeCPU = workerNodeInfo.get(
                'cpu', os.environ['WORKER_DEFAULT_CPU'])
            workerNodeMemory = workerNodeInfo.get(
                'memory', os.environ['WORKER_DEFAULT_MEMORY'])
            workerNodeStorage = workerNodeInfo.get(
                'disk', os.environ['WORKER_DEFAULT_STORAGE'])
            NodeInit(workerNodeName, workerNodeCPU, workerNodeMemory,
                     workerNodeStorage, NodeType.WORKER, masterNodeToken, masterNodeIP)
            workerNodeIP = getNodeIP(workerNodeName)
            workerConfig[i]["ip"] = workerNodeIP
            print(self.getNormalMessage(f"Complete to build worker node : {workerNodeName} ..."))

        self.saveConfig(Assets.MASTER_CONFIG, masterConfig)
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

        # Make kube config directory if not exist
        if not os.path.exists(Assets.KUBE_CONFIG_DIR):
            os.mkdir(Assets.KUBE_CONFIG_DIR)

        # If kubeconfig exist, make it copy
        if os.path.exists(Assets.KUBE_CONFIG):
            os.rename(Assets.KUBE_CONFIG,
                      f"{Assets.KUBE_CONFIG_DIR}/config_cp")
            print(self.getSpecialMessage(f"Saving previous kubectl config file as {Assets.KUBE_CONFIG_DIR}/config_cp ..."))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/getKubeConfig.sh",
                       masterNodeName, masterNodeIP, Assets.KUBE_CONFIG])

    def terminate_cluster(self):
        print("It may take a while... please wait")
        # Get master node config
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)

        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        instanceList = list(workerConfig.keys())
        instanceList.append(Assets.MASTER_NODE_KEY)
        for i in instanceList:
            i = self.getNodeName(i)
            print(self.getNormalMessage(f"Terminating node : {i}"))
            subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/terminateCluster.sh", i])

        if self.typeChecker(masterConfig[Assets.MASTER_NODE_KEY], dict):
            if "ip" in masterConfig[Assets.MASTER_NODE_KEY]:
                masterConfig[Assets.MASTER_NODE_KEY]["ip"] = ""
            if "token" in masterConfig[Assets.MASTER_NODE_KEY]:
                masterConfig[Assets.MASTER_NODE_KEY]["token"] = ""

        for i, j in workerConfig.items():
            if self.typeChecker(j, dict):
                if "ip" in j:
                    workerConfig[i]["ip"] = ""
        self.saveConfig(Assets.MASTER_CONFIG, masterConfig)
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/purgeInstance.sh"])
        print(self.getNormalMessage("Complete to terminate cluster!"))

    def add_node(self, name):
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)
        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        # name should be same with as in config file
        if name not in workerConfig.keys():
            raise exceptions.WrongArgumentGiven(f"Name '{name}' not found in worker config")

        workerNodeName = self.getNodeName(name)

        # Check instance name in use
        if not self.checkInstanceNameNotInUse(workerNodeName):
            raise exceptions.InvalidNodeGenerationDetected(
                self.getCriticalMessage(f"Name with '{workerNodeName}' already in use! Ignore generating worker-node config '{name}'"))

        if not self.typeChecker(workerConfig[name], dict):
            raise exceptions.InvalidConfigType(dict)

        workerNodeInfo = workerConfig[name]
        workerNodeCPU = workerNodeInfo.get(
            'cpu', os.environ['WORKER_DEFAULT_CPU'])
        workerNodeMemory = workerNodeInfo.get(
            'memory', os.environ['WORKER_DEFAULT_MEMORY'])
        workerNodeStorage = workerNodeInfo.get(
            'disk', os.environ['WORKER_DEFAULT_STORAGE'])
        token = masterConfig[Assets.MASTER_NODE_KEY]["token"]
        ip = masterConfig[Assets.MASTER_NODE_KEY]["ip"]
        if (not ip) or (not token):
            raise exceptions.MasterNodeNotFound()
        print(self.getNormalMessage(f"Initiating worker node : {workerNodeName} ..."))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", workerNodeName, workerNodeCPU,
                       workerNodeMemory, workerNodeStorage, NodeType.WORKER, token, ip], stdout=subprocess.PIPE)
        print(self.getNormalMessage(f"Complete to build worker node : {workerNodeName} ..."))
        workerConfig[name]["ip"] = subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/getNodeIP.sh", workerNodeName], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

    def connectShell(self,name):
        node_name = self.getNodeName(name)
        if self.checkInstanceNameNotInUse(node_name):
            raise exceptions.NodeNotFound(node_name)
        subprocess.run(["bash",f"{Assets.SCRIPT_PATH}/connectShell.sh",node_name])

    def deleteNode(self,name):
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        node_name = self.getNodeName(name)
        if node_name == Assets.MASTER_NODE_KEY:
            raise exceptions.IllegalControlException("Can't delete worker node by alone!")

        if self.checkInstanceNameNotInUse(node_name):
            raise exceptions.NodeNotFound(node_name)
        print(self.getNormalMessage(f"Delete node '{node_name}' from cluster"))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/deleteNode.sh",Assets.MASTER_NODE_KEY,node_name])
        print(self.getNormalMessage(f"Complete to delete node '{node_name}' from cluster"))
        print(self.getNormalMessage(f"Terminating instance : '{node_name}'" ))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/terminateCluster.sh", node_name])
        print(self.getNormalMessage(f"Complete to terminate instance : '{node_name}'"))
        workerConfig[name]["ip"] = ""
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/purgeInstance.sh"])

