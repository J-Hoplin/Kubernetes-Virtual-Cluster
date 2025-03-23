import subprocess
from kluster.utils import logger


def cleanup_kubeconfig(nodes):
    try:
        for node_name, node_type in nodes:
            if node_type == "master":
                context_name = f"k3s-{node_name}"
                logger.log(f"Removing kubeconfig entries for: {context_name}")

                subprocess.run(
                    ["kubectl", "config", "delete-context", context_name],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["kubectl", "config", "delete-cluster", context_name],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["kubectl", "config", "delete-user", context_name],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clean kubeconfig: {e}")
        return False
