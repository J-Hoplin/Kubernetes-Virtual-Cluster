import subprocess
from kluster.utils import logger


def destroy_node(node_name):
    try:
        subprocess.run(["multipass", "stop", node_name], check=True)
        subprocess.run(["multipass", "delete", node_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to destroy node {node_name}: {e}")
        return False


def purge_multipass():
    try:
        subprocess.run(["multipass", "purge"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to purge instances: {e}")
        return False
