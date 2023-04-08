import subprocess
import json
import os
from exception import exceptions
from colorama import Fore, Style


class Assets(object):
    MASTER_NODE_KEY = 'master-node'
    MASTER_CONFIG = './nodes/master/config.json'
    WORKER_CONFIG = './nodes/worker/config.json'
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

    def cluster_init(self):
        os.system('clear')

        def NodeInit(name, cpu, memory, disk, tp, *args):
            if tp == NodeType.MASTER:
                subprocess.run(["bash", "./nodes/nodeInit.sh", name,
                               cpu, memory, disk, tp], stdout=subprocess.PIPE)
            elif tp == NodeType.WORKER:
                token, ip = args
                subprocess.run(["bash", "./nodes/nodeInit.sh", name, cpu,
                               memory, disk, tp, token, ip], stdout=subprocess.PIPE)
            else:
                raise exceptions.IllegalControlException("Invalid node type")

        def getNodeIP(name):
            return subprocess.run(["bash", "./nodes/getNodeIP.sh", name], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        if not os.path.exists('./nodes'):
            raise exceptions.DirectoryNotFound('nodes')

        # Get master node config
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)

        print(Fore.GREEN + "Complete to load : Master config" + Style.RESET_ALL)

        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        print(Fore.GREEN + "Complete to load : Worker config" + Style.RESET_ALL)

        # Initialize master node config

        if Assets.MASTER_NODE_KEY not in masterConfig:
            raise exceptions.MasterNodeConfigNotFound()

        print(Fore.GREEN + "Initiating master node ..." + Style.RESET_ALL)
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
            ["bash", "./nodes/getMasterToken.sh", masterNodeName], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        masterConfig[masterNodeName]["token"] = masterNodeToken

        if (not masterNodeIP) or (not masterNodeToken):
            raise exceptions.ImproperMasterNodeGenerated()

        print(f"Master Node IP : {masterNodeIP}")
        print(f"Master Node Token : {masterNodeToken}")
        print(Fore.GREEN + "Complete to build master node ..." + Style.RESET_ALL)

        # Initialize worker node config
        for i, j in workerConfig.items():
            workerNodeName: str = "-".join(i.split(" "))
            print(
                Fore.GREEN + f"Initiating worker node : {workerNodeName} ..." + Style.RESET_ALL)
            workerNodeInfo: dict = j

            if not self.typeChecker(workerNodeInfo, dict):
                print(
                    Fore.RED + f"Invalid config type of worker node : {workerNodeName}! Ignore generation" + Style.RESET_ALL)
                continue

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
            print(
                Fore.GREEN + f"Complete to build worker node : {workerNodeName} ..." + Style.RESET_ALL)

        self.saveConfig(Assets.MASTER_CONFIG, masterConfig)
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

        # Make kube config directory if not exist
        if not os.path.exists(Assets.KUBE_CONFIG_DIR):
            os.mkdir(Assets.KUBE_CONFIG_DIR)

        # If kubeconfig exist, make it copy
        if os.path.exists(Assets.KUBE_CONFIG):
            os.rename(Assets.KUBE_CONFIG,
                      f"{Assets.KUBE_CONFIG_DIR}/config_cp")
            print(
                Fore.GREEN + f"Saving previous kubectl config file as {Assets.KUBE_CONFIG_DIR}/config_cp ..." + Style.RESET_ALL)
        subprocess.run(["bash", "./nodes/getKubeConfig.sh",
                       masterNodeName, masterNodeIP])

    def terminate_cluster(self):
        print("It may take a while... please wait")
        # Get master node config
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)

        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)

        instanceList = list(workerConfig.keys())
        instanceList.append(Assets.MASTER_NODE_KEY)
        for i in instanceList:
            i = "-".join(i.split(" "))
            print(Fore.GREEN + f"Terminating node : {i}")
            subprocess.run(["bash", "./nodes/terminateCluster.sh", i])

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

        subprocess.run(["multipass", "purge"])
        print(Fore.GREEN + "Complete to terminate cluster!")

    def add_node(self, name):
        masterConfig: dict = self.readConfig(Assets.MASTER_CONFIG)
        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)
        if name not in workerConfig.keys():
            raise exceptions.WrongArgumentGiven()

        if not self.typeChecker(workerConfig[name], dict):
            raise exceptions.InvalidConfigType()

        workerNodeName = "-".join(name.split(" "))
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
        print(
            Fore.GREEN + f"Initiating worker node : {workerNodeName} ..." + Style.RESET_ALL)
        subprocess.run(["bash", "./nodes/nodeInit.sh", workerNodeName, workerNodeCPU,
                       workerNodeMemory, workerNodeStorage, NodeType.WORKER, token, ip], stdout=subprocess.PIPE)
        print(
            Fore.GREEN + f"Complete to build worker node : {workerNodeName} ..." + Style.RESET_ALL)
        workerConfig[name]["ip"] = subprocess.run(
            ["bash", "./nodes/getNodeIP.sh", workerNodeName], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        self.saveConfig(Assets.WORKER_CONFIG, workerConfig)

    def connectShell(self,name):
        # Get worker node config
        workerConfig: dict = self.readConfig(Assets.WORKER_CONFIG)
        nodeList:list = list(workerConfig.keys())
        nodeList.append(Assets.MASTER_NODE_KEY)
        nodeList = list(map(lambda x: "-".join(x.split(" ")),nodeList))
        name = "-".join(name.split(" "))
        if name not in nodeList:
            raise exceptions.NodeNotFound(name)
        subprocess.run(["bash","./nodes/connectShell.sh",name])