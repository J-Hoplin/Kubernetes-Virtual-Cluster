import subprocess,json,os
from exception import exceptions
from colorama import Fore,Style

class Assets(object):
    MASTER_NODE_KEY = 'master-node'
    MASTER_CONFIG = './nodes/master/config.json'
    WORKER_CONFIG = './nodes/worker/config.json'
    KUBE_CONFIG_DIR=f"{os.environ['HOME']}/.kube"
    KUBE_CONFIG = f"{os.environ['HOME']}/.kube/config"

class NodeType(object):
    MASTER='master'
    WORKER='worker'

class Resolver(object):
    def __init__(self):
        pass
    def cluster_init(self):
        os.system('clear')
        def NodeInit(name,cpu,memory,disk,type,*args):
            if type == NodeType.MASTER:
                subprocess.run(["bash","./nodes/nodeInit.sh",name,cpu,memory,disk,type], stdout=subprocess.PIPE)
            elif type == NodeType.WORKER:
                token,ip = args
                subprocess.run(["bash","./nodes/nodeInit.sh",name,cpu,memory,disk,type,token,ip], stdout=subprocess.PIPE)
            else:
                raise exceptions.IllegalControlException("Invalid node type")
        def getNodeIP(name):
            return subprocess.run(["bash","./nodes/getNodeIP.sh",name],stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        if not os.path.exists('./nodes'):
            raise exceptions.DirectoryNotFound('nodes')

        # Get master node config
        with open(Assets.MASTER_CONFIG,'r') as config:
            masterConfig:dict = json.load(config)

        print(Fore.GREEN + "Complete to load : Master config" + Style.RESET_ALL)

        # Get worker node config
        with open(Assets.WORKER_CONFIG,'r') as config:
            workerConfig:dict = json.load(config)

        print(Fore.GREEN + "Complete to load : Worker config" + Style.RESET_ALL)

        # Initialize master node config

        if Assets.MASTER_NODE_KEY not in masterConfig:
            raise exceptions.MasterNodeConfigNotFound()

        print(Fore.GREEN + "Initiating master node ..." + Style.RESET_ALL)
        masterNodeName:str = Assets.MASTER_NODE_KEY
        masterNodeInfo:dict = masterConfig[masterNodeName]
        masterNodeCPU = masterNodeInfo.get('cpu',os.environ['MASTER_DEFAULT_CPU'])
        masterNodeMemory= masterNodeInfo.get('memory',os.environ['MASTER_DEFAULT_MEMORY'])
        masterNodeStorage= masterNodeInfo.get('disk',os.environ['MASTER_DEFAULT_STORAGE'])
        NodeInit(masterNodeName,masterNodeCPU,masterNodeMemory,masterNodeStorage,NodeType.MASTER)

        masterNodeIP = getNodeIP(masterNodeName)
        masterConfig[masterNodeName]["ip"] = masterNodeIP
        masterNodeToken = subprocess.run(["bash","./nodes/getMasterToken.sh",masterNodeName],stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        print(f"Master Node IP : {masterNodeIP}")
        print(f"Master Node Token : {masterNodeToken}")
        print(Fore.GREEN + "Complete to build master node ..." + Style.RESET_ALL)

        # Initialize worker node config
        for i,j in workerConfig.items():
            workerNodeName:str = i
            print(Fore.GREEN + f"Initiating worker node : {workerNodeName} ..." + Style.RESET_ALL)
            workerNodeInfo:dict = j
            workerNodeCPU = workerNodeInfo.get('cpu',os.environ['WORKER_DEFAULT_CPU'])
            workerNodeMemory = workerNodeInfo.get('memory',os.environ['WORKER_DEFAULT_MEMORY'])
            workerNodeStorage = workerNodeInfo.get('disk',os.environ['WORKER_DEFAULT_STORAGE'])
            NodeInit(workerNodeName,workerNodeCPU,workerNodeMemory,workerNodeStorage,NodeType.WORKER,masterNodeToken,masterNodeIP)
            workerNodeIP = getNodeIP(workerNodeName)
            workerConfig[workerNodeName]["ip"] = workerNodeIP
            print(Fore.GREEN + f"Complete to build master node : {workerNodeName} ..." + Style.RESET_ALL)

        with open(Assets.MASTER_CONFIG, 'w') as config:
            json.dumps(masterConfig,indent=4)
            json.dump(masterConfig,config)

        with open(Assets.WORKER_CONFIG, 'w') as config:
            json.dumps(workerConfig,indent=4)
            json.dump(workerConfig,config)

        # Make kube config directory if not exist
        if not os.path.exists(Assets.KUBE_CONFIG_DIR):
            os.mkdir(Assets.KUBE_CONFIG_DIR)

        # If kubeconfig exist, make it copy
        if os.path.exists(Assets.KUBE_CONFIG):
            os.rename(Assets.KUBE_CONFIG,f"{Assets.KUBE_CONFIG_DIR}/config_cp")
            print(Fore.GREEN + f"Saving previous kubectl config file as {Assets.KUBE_CONFIG_DIR}/config_cp ..." + Style.RESET_ALL)
        subprocess.run(["bash","./nodes/getKubeConfig.sh",masterNodeName])
    def terminate_cluster(self):
        # Get worker node config
        with open(Assets.WORKER_CONFIG, 'r') as config:
            workerConfig: dict = json.load(config)
        instanceList = list(workerConfig.keys())
        instanceList.append(Assets.MASTER_NODE_KEY)
        for i in instanceList:
            subprocess.run(["bash","./nodes/terminateCluster.sh",i])
        subprocess.run(["multipass","purge"])
        print(Fore.GREEN + "Complete to terminate cluster!")
