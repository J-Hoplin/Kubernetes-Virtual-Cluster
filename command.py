import argparse,dotenv
from app import Resolver
from exception import exceptions

env_file = dotenv.find_dotenv()
dotenv.load_dotenv(env_file)

resolver = Resolver()
#
# parser = argparse.ArgumentParser(description="K3S + Multipass virtual cluster")
# parser.add_argument("-c","--cluster",help="Initiate cluster with : 'init' / Terminate cluster with : 'terminate'",required=True)
#
# argList = parser.parse_args()
#
# if argList.cluster == "init":
#     resolver.cluster_init()
# elif argList.cluster == "terminate":
#     resolver.terminate_cluster()
# else:
#     raise exceptions.WrongArgumentGiven()

resolver.cluster_init()