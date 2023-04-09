import argparse
import dotenv
from app import Resolver
from exception import exceptions

env_file = dotenv.find_dotenv()
dotenv.load_dotenv(env_file)

resolver = Resolver()

parser = argparse.ArgumentParser(description="K3S + Multipass virtual cluster")
parser.add_argument(
    "-c", "--cluster", help="""
    Initiate cluster with : 'init'
    Terminate cluster with : 'terminate'
    Add node with : 'add'
    Delete node with : 'delete'
    Connect to node's shell with : 'shell'
    """, required=True)
parser.add_argument(
    "-n", "--name", help="Required if you use option of '-c' as 'add' and 'shell'. Node's name"
)

argList = parser.parse_args()

try:
    if argList.cluster == "init":
        resolver.cluster_init()
    elif argList.cluster == "terminate":
        resolver.terminate_cluster()
    elif argList.cluster == "add":
        if not argList.name:
            raise exceptions.RequiredCommandLineOptionLost('-n')
        resolver.add_node(argList.name)
    elif argList.cluster == "shell":
        if not argList.name:
            raise exceptions.RequiredCommandLineOptionLost('-n')
        resolver.connectShell(argList.name)
    elif argList.cluster == "delete":
        if not argList.name:
            raise exceptions.RequiredCommandLineOptionLost('-n')
        resolver.deleteNode(argList.name)
    else:
        raise exceptions.WrongArgumentGiven()
except Exception as e:
    print(str(e))
