import subprocess
import time
import random
import string
from kluster.utils import logger


def setup_single_master_cluster(connection, cursor, master_nodes, worker_nodes,kubernetes_version):
    logger.log("🔄 Mode: Single master node cluster")

    master_name = next(iter(master_nodes.keys()))
    cursor.execute("SELECT ip FROM nodes WHERE name = ?", (master_name,))
    master_ip = cursor.fetchone()[0]

    token = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    master_cmd = f"curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='{kubernetes_version}' K3S_TOKEN='{token}' sh -"
    result = run_multipass_cmd(master_name, master_cmd)
    if not result:
        return False

    logger.log(f"✅Master node initialized: {master_name}")

    cursor.execute("UPDATE nodes SET token = ? WHERE name = ?", (token, master_name))
    connection.commit()

    setup_worker_nodes(connection, cursor, master_ip, token, worker_nodes, kubernetes_version)

    return True


def setup_ha_master_cluster(connection, cursor, master_nodes, worker_nodes,kubernetes_version):
    logger.log("🔄 Mode: High availability cluster")

    master_names = list(master_nodes.keys())
    first_master = master_names[0]

    cursor.execute("SELECT ip FROM nodes WHERE name = ?", (first_master,))
    first_master_ip = cursor.fetchone()[0]

    token = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    master_init_cmd = f"curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='{kubernetes_version}' K3S_TOKEN='{token}' sh -s - server --cluster-init"
    result = run_multipass_cmd(first_master, master_init_cmd)
    if not result:
        return False

    logger.log(f"✅ Primary master node: {first_master}")
    for master_name in master_names:
        cursor.execute(
            "UPDATE nodes SET token = ? WHERE name = ?", (token, master_name)
        )
    connection.commit()

    logger.log("Pending: Waiting for primary master node")
    time.sleep(15)

    for master_name in master_names[1:]:
        cursor.execute("SELECT ip FROM nodes WHERE name = ?", (master_name,))
        # K3S는 Master Node는 Server 모드로 일반 Worker Node는 Agent 모드로 설정해줘야함
        # https://docs.k3s.io/cli/server
        # https://docs.k3s.io/cli/agent
        join_cmd = f"curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='{kubernetes_version}' K3S_TOKEN='{token}' sh -s - server --server https://{first_master_ip}:6443"
        result = run_multipass_cmd(master_name, join_cmd)
        if not result:
            logger.warn(f"⚠️Fail to initialize master node: {master_name}")
            continue

        logger.log(f"✅Master node join to cluster: {master_name} ")
    setup_worker_nodes(connection, cursor, first_master_ip, token, worker_nodes,kubernetes_version)

    return True


def setup_worker_nodes(connection, cursor, master_ip, token, worker_nodes, kubernetes_version):
    if not worker_nodes:
        logger.log("🤔No worker nodes to configure")
        return True

    logger.log("🔄 Setting up worker nodes...")
    for worker_name in worker_nodes.keys():
        join_cmd = f"curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL='{kubernetes_version}' K3S_TOKEN='{token}' K3S_URL='https://{master_ip}:6443' sh -"
        result = run_multipass_cmd(worker_name, join_cmd)
        if not result:
            logger.warn(f"❌Failed to join worker node {worker_name}")
            continue

        logger.log(f"✨Worker node {worker_name} joined the cluster")

    return True


def run_multipass_cmd(node_name, command):
    cmd = ["multipass", "exec", node_name, "--", "bash", "-c", command]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"Error running on {node_name}: {result.stderr}")
        return False

    return True
