import subprocess
import json
from cluster.utils import logger


def create_vms(connection, cursor, master_nodes, worker_nodes):
    logger.log("Assign instance per node...", context="Multipass")
    all_nodes = {**master_nodes, **worker_nodes}

    for node_name, node_config in all_nodes.items():
        cpu = node_config.get("cpu", 2 if node_config.get("type") == "master" else 1)
        memory = node_config.get(
            "memory", 2048 if node_config.get("type") == "master" else 1024
        )
        disk = node_config.get("disk", 10)

        logger.log(f"✨ Creating VM for {node_name}", context="Multipass")
        cmd = [
            "multipass",
            "launch",
            "--name",
            node_name,
            "--cpus",
            str(cpu),
            "--memory",
            f"{memory}M",
            "--disk",
            f"{disk}G",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(
                f"Fail to create instance {node_name}: {result.stderr}",
                context="Multipass",
            )
            return False

        ip_cmd = ["multipass", "info", node_name, "--format", "json"]
        ip_result = subprocess.run(ip_cmd, capture_output=True, text=True)
        if ip_result.returncode == 0:
            info = json.loads(ip_result.stdout)
            ip = info.get("info", {}).get(node_name, {}).get("ipv4", [""])[0]

            cursor.execute("UPDATE nodes SET ip = ? WHERE name = ?", (ip, node_name))
            connection.commit()

            logger.log(
                f"Instance {node_name} created with IP: {ip}", context="Multipass"
            )
        else:
            logger.warn(
                f"Warning: Could not get IP for {node_name}", context="Multipass"
            )

    return True
