import subprocess
import os
from exception import exceptions
from utils.utility import Utility
from decorator.instanceNameAlreadyTakenChecker import InstanceNameAlreadyTakenChecker
from decorator.instanceExistChecker import InstanceExistChecker


class Assets(object):
    MASTER_NODE_KEY = 'master-node'
    MASTER_CONFIG = './nodes/master/config.json'
    WORKER_CONFIG = './nodes/worker/config.json'
    SCRIPT_PATH = './scripts'
    KUBE_CONFIG_DIR = f"{os.environ['HOME']}/.kube"
    KUBE_CONFIG = f"{os.environ['HOME']}/.kube/config"
    KWARGS_WORKER_NODE_KEY = 'node_name'


class NodeType(object):
    MASTER = 'master'
    WORKER = 'worker'


class Resolver(Utility):
    def __init__(self):
        pass

    def cluster_init(self, version):
        os.system('clear')

        def NodeInit(name, cpu, memory, disk, tp, *args):
            if tp == NodeType.MASTER:
                subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", name,
                               cpu, memory, disk, tp, version], stdout=subprocess.PIPE)
            elif tp == NodeType.WORKER:
                token, ip = args
                subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", name, cpu,
                               memory, disk, tp, token, ip, version], stdout=subprocess.PIPE)
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
                self.getCriticalMessage(
                    f"Instance with '{Assets.MASTER_NODE_KEY}' already in use! Stop generating cluster.")
            )

        print(self.getNormalMessage(
            f"Initiating {Assets.MASTER_NODE_KEY} ..."))
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
        print("\n")
        print(self.getSpecialMessage(f"[[ Master node config values ]]"))
        print(self.getSpecialMessage(f"Master Node IP : {masterNodeIP}"))
        print(self.getSpecialMessage(
            f"Master Node Token : {masterNodeToken}\n"))
        print(self.getNormalMessage("Complete to build master node ..."))

        print("\n")
        # Initialize worker node config
        nodeCount = len(workerConfig)
        failedNodeCount = 0

        for index, items in enumerate(workerConfig.items()):
            i, j = items
            if not self.validateNodeName(i):
                print(self.getCriticalMessage(
                    f"Fail to generate node - Illegal node name config : {i}"))
                failedNodeCount += 1
                continue
            workerNodeName: str = i
            print(self.getNormalMessage(
                f"[[ Initializing Node : {i} ({index + 1}/{nodeCount}) ]]"))
            if not self.checkInstanceNameNotInUse(workerNodeName):
                print(self.getCriticalMessage(
                    f"Instance with name '{workerNodeName}' already in use! Ignore generating worker-node config '{i}'"))
                continue

            workerNodeInfo: dict = j

            if not self.typeChecker(workerNodeInfo, dict):
                print(self.getCriticalMessage(
                    f"Invalid config type of worker node : {workerNodeName}!"))
                continue
            print(self.getNormalMessage(
                f"Initiating worker node : {workerNodeName} ..."))
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
            print(self.getNormalMessage(
                f"Complete to build worker node : {workerNodeName} ...\n"))

        self.saveConfig(Assets.MASTER_CONFIG, masterConfig)
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

        # Make kube config directory if not exist
        if not os.path.exists(Assets.KUBE_CONFIG_DIR):
            os.mkdir(Assets.KUBE_CONFIG_DIR)

        # If kubeconfig exist, make it copy
        if os.path.exists(Assets.KUBE_CONFIG):
            os.rename(Assets.KUBE_CONFIG,
                      f"{Assets.KUBE_CONFIG_DIR}/config_cp")
            print(self.getSpecialMessage(
                f"Saving previous kubectl config file as {Assets.KUBE_CONFIG_DIR}/config_cp ..."))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/getKubeConfig.sh",
                       masterNodeName, masterNodeIP, Assets.KUBE_CONFIG])

        print(f"""\n
{self.getNormalMessage(f"Success - {nodeCount - failedNodeCount}/{nodeCount}")}
{self.getCriticalMessage(f"Failed - {failedNodeCount}/{nodeCount}",False)}
        """)

        print(self.getSpecialMessage(f"🚀 Cluster ready!"))

    def terminate_cluster(self):
        print("It may take a while... please wait")
        # Get master node config
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)

        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        instanceList = list(workerConfig.keys())
        instanceList.append(Assets.MASTER_NODE_KEY)
        for i in instanceList:
            if not self.validateNodeName(i):
                print(self.getCriticalMessage(
                    f"Illegal node name config : {i}. Ignore this node from terminate process."))
                continue
            print(self.getNormalMessage(f"Terminating node : {i}"))
            subprocess.run(
                ["bash", f"{Assets.SCRIPT_PATH}/terminateCluster.sh", i])

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

    @InstanceNameAlreadyTakenChecker()
    def add_node(self, name, version, **kwargs):
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)
        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        # name should be same with as in config file
        if name not in workerConfig.keys():
            raise exceptions.WrongArgumentGiven(
                f"Name '{name}' not found in worker config")

        workerNodeName = kwargs[Assets.KWARGS_WORKER_NODE_KEY]

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
        print(self.getNormalMessage(
            f"Initiating worker node : {workerNodeName} ..."))
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/nodeInit.sh", workerNodeName, workerNodeCPU,
                       workerNodeMemory, workerNodeStorage, NodeType.WORKER, token, ip, version], stdout=subprocess.PIPE)
        print(self.getNormalMessage(
            f"Complete to build worker node : {workerNodeName} ..."))
        workerConfig[name]["ip"] = subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/getNodeIP.sh", workerNodeName], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

    @InstanceExistChecker()
    def connectShell(self, name, **kwargs):
        node_name = kwargs[Assets.KWARGS_WORKER_NODE_KEY]
        subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/connectShell.sh", node_name])

    @InstanceExistChecker()
    def deleteNode(self, name, **kwargs):
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        node_name = kwargs[Assets.KWARGS_WORKER_NODE_KEY]
        if node_name == Assets.MASTER_NODE_KEY:
            raise exceptions.IllegalControlException(
                "Can't delete worker node by alone!")

        print(self.getNormalMessage(f"Delete node '{node_name}' from cluster"))
        subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/deleteNode.sh", Assets.MASTER_NODE_KEY, node_name])
        print(self.getNormalMessage(
            f"Complete to delete node '{node_name}' from cluster"))
        print(self.getNormalMessage(f"Terminating instance : '{node_name}'"))
        subprocess.run(
            ["bash", f"{Assets.SCRIPT_PATH}/terminateCluster.sh", node_name])
        print(self.getNormalMessage(
            f"Complete to terminate instance : '{node_name}'"))
        workerConfig[name]["ip"] = ""
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)
        subprocess.run(["bash", f"{Assets.SCRIPT_PATH}/purgeInstance.sh"])
