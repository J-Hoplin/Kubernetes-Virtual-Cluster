import os
import json
import sqlite3
import re
import subprocess
from kluster.constant import CLUSTER_PATH, SQLITE_PATH, DEFAULT_CONFIG_PATH
from kluster.command.actions.init_cluster import (
    setup_single_master_cluster,
    setup_ha_master_cluster,
)
from kluster.command.actions.init_multipass import check_and_download_image, create_vms
from kluster.command.actions.destroy import run as destroy_run
from kluster.utils.dependency import require_dependencies
from kluster.utils import logger


def config_deserializer(config_path):
    if not os.path.exists(config_path):
        logger.error(f"❌ Config file does not exist: {config_path}")
        return None

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON format error: {e.msg}")
        return None


def check_existing_cluster(db_path, force=False):
    """
    SQLite에 상태를 관리중인 cluster가 있는지 확인함

    옵션 force가 주어진 경우에는 그냥 강제 진행
    """
    if not os.path.exists(db_path) or os.path.getsize(db_path) <= 0:
        return True

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM sqlite_master WHERE type='table' AND name='nodes'"
            )
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM nodes")
                count = cursor.fetchone()[0]

                if count > 0:
                    if force:
                        logger.warn(
                            "⚠️Existing cluster state cleared due to force option"
                        )
                        args = type("Args", (), {"force": True})()
                        destroy_run(args)
                        return True
                    else:
                        logger.warn(f"Warning: {count} nodes are already registered.")
                        confirmation = input(
                            "⚠️ Do you want to delete existing cluster state and reinitialize? (Y/N): "
                        )
                        if confirmation.lower() != "y":
                            logger.warn("Unable to proceed with existing cluster data.")
                            return False
                        args = type("Args", (), {"force": True})()
                        destroy_run(args)
                        return True
        return True
    except sqlite3.Error as e:
        logger.error(f"Error while checking database: {e}")
        return False


def initialize_database(db_path):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        node_type = ("master", "worker")
        cursor.execute("DROP TABLE IF EXISTS nodes")
        cursor.execute(
            f"""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            node_type TEXT NOT NULL CHECK(node_type IN {node_type}),
            cpu INTEGER NOT NULL,
            memory INTEGER NOT NULL,
            disk INTEGER NOT NULL,
            ip TEXT,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        return connection, cursor
    except sqlite3.Error as e:
        logger.error(f"Error while initializing database: {e}")
        return None, None


def validate_node_config(node_name, node_config, valid_node_types):
    """
    노드 이름은 Multipass에서 허용하는 형식을 따름.

    사실 모든 이름 유형이 검사된지는 모르겠으나 일단 Go로 작성된 버전꺼 그대로 사용하도록 하고
    필요하면 정규식 수정 필요할듯함
    """
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9-]*$", node_name):
        logger.error(f"Invalid node name: {node_name}")
        return False

    node_type = node_config.get("type", "").lower()
    if node_type not in valid_node_types:
        logger.error("Node type must be either 'master' or 'worker'")
        return False

    return True


def process_node_resources(node_name, node_type, node_config):
    """
    기본값은 아래와 같음.
    물론 Worker Node가 일반적으로 더 많은 리소스를 요구하지만
    일단 고민해보고 나중에 재설정하기

    Memory 단위는 MB
    Disk 단위는 GB
    -> 나중에 파싱하는거 간단히 넣기

    Master Node

    - CPU: 2
    - Memory: 2048
    - Disk: 10

    Worker Node

    - CPU: 1
    - Memory: 1024
    - Disk: 10
    """
    cpu = 2 if node_type == "master" else 1
    memory = 2048 if node_type == "master" else 1024
    disk = 10

    try:
        cpu = int(node_config.get("cpu", cpu))
        memory = int(node_config.get("memory", memory))
        disk = int(node_config.get("disk", disk))
        return cpu, memory, disk
    except ValueError:
        logger.warn("Hint: CPU, Memory, Disk must be integer values")
        logger.error(f"Invalid value found while initializing '{node_name}' resources")
        return None, None, None


def insert_node_to_db(cursor, node_name, node_type, cpu, memory, disk, node_config):
    cursor.execute(
        """
            INSERT INTO nodes (name, node_type, cpu, memory, disk, ip, token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
        (
            node_name,
            node_type,
            cpu,
            memory,
            disk,
            node_config.get("ip", ""),
            node_config.get("token", ""),
        ),
    )


def get_nodes_by_type(cursor):
    cursor.execute("SELECT name, node_type, ip FROM nodes")
    nodes_data = cursor.fetchall()

    master_nodes = {}
    worker_nodes = {}

    for node in nodes_data:
        node_name, node_type, ip = node
        cursor.execute(
            "SELECT cpu, memory, disk FROM nodes WHERE name = ?", (node_name,)
        )
        cpu, memory, disk = cursor.fetchone()

        node_config = {
            "type": node_type,
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "ip": ip,
        }

        if node_type == "master":
            master_nodes[node_name] = node_config
        else:
            worker_nodes[node_name] = node_config

    return master_nodes, worker_nodes


def verify_cluster_status(master_name):
    logger.log("Verifying cluster status...")
    cmd = [
        "multipass",
        "exec",
        master_name,
        "--",
        "sudo",
        "kubectl",
        "get",
        "nodes",
        "-o",
        "wide",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        pass
    else:
        logger.warn("⚠️Could not verify cluster status")


def get_master_node_ips(connection, cursor, master_nodes):
    master_node_params = []
    logger.log("👀Retrieving master node IPs...")
    for master_name, master_info in master_nodes.items():
        ip_cmd = ["multipass", "info", master_name, "--format", "json"]
        ip_result = subprocess.run(ip_cmd, capture_output=True, text=True)

        if ip_result.returncode == 0:
            info = json.loads(ip_result.stdout)
            master_ip = info.get("info", {}).get(master_name, {}).get("ipv4", [""])[0]

            cursor.execute(
                "UPDATE nodes SET ip = ? WHERE name = ?", (master_ip, master_name)
            )
            connection.commit()
            master_node_params.append(f"{master_name}:{master_ip}")
        else:
            cursor.execute("SELECT ip FROM nodes WHERE name = ?", (master_name,))
            result = cursor.fetchone()
            if result and result[0]:
                master_ip = result[0]
                master_node_params.append(f"{master_name}:{master_ip}")
            else:
                logger.warn(f"⚠️ Could not retrieve IP for {master_name}")

    return master_node_params


def update_kubeconfig(master_node_params):
    script_path = os.path.join(CLUSTER_PATH, "scripts", "init_config_update.sh")

    if not os.path.exists(script_path):
        logger.warn(f"Script not found at {script_path}")
        return False

    if not os.access(script_path, os.X_OK):
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            logger.error(f"Fail to set execute permission: {e}")
            return False

    if not master_node_params:
        logger.error("Fail to update kubeconfig")
        return False

    cmd = [script_path] + master_node_params

    try:
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            logger.error(f"Fail to update kubeconfig: {process.stderr}")
            return False

        logger.log("✅ Kubeconfig updated")
        logger.log(
            """
Switch kubectl context to master node context ("k3s-<master node name>")
Command:
    kubectl config use-context <context-name>
"""
        )
        return True

    except Exception as e:
        logger.error(f"Fail to update kubeconfig: {e}")
        return False


@require_dependencies()
def run(args):
    if not os.path.isabs(args.config):
        current_dir_config = os.path.join(os.getcwd(), args.config)
        if os.path.exists(current_dir_config):
            config_path = current_dir_config
        else:
            config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = args.config

    config = config_deserializer(config_path)
    if not config:
        return 1

    db_path = SQLITE_PATH

    if not check_existing_cluster(db_path, args.force):
        return 1

    connection, cursor = initialize_database(db_path)
    if not connection or not cursor:
        return 1

    try:
        master_node_count = 0
        worker_node_count = 0
        """
        Config 포맷 예시

        - k3s_version: https://github.com/k3s-io/k3s/releases
        - ubuntu_version: 설치된 multipass에서 지원하는 버전들로만

        {
            "k3s_version": "v1.26.6+k3s1",
            "ubuntu_version": "22.04",
            "nodes": {
                "master-1": {
                    "type": "master", -> enum('master', 'worker')
                    "cpu": 2,
                    "memory": 2048,
                    "disk": 10,
                    "ip": ""
                }
            }
        }
        """
        kubernetes_version = config.get("k3s_version")
        ubuntu_version = config.get("ubuntu_version", "22.04")
        logger.log(f"Kubernetes version: {kubernetes_version}")
        logger.log(f"Ubuntu version: {ubuntu_version}")

        check_and_download_image(ubuntu_version)

        if not kubernetes_version:
            logger.error("Error: Kubernetes version must be specified.")
            connection.close()
            return 1

        node_config_dict = config.get("nodes", {})
        valid_node_types = ("master", "worker")

        for node_name, node_config in node_config_dict.items():
            if not validate_node_config(node_name, node_config, valid_node_types):
                connection.close()
                return 1

            node_type = node_config.get("type", "").lower()

            if node_type == "master":
                master_node_count += 1
            else:
                worker_node_count += 1

            cpu, memory, disk = process_node_resources(
                node_name, node_type, node_config
            )
            if cpu is None:
                connection.close()
                return 1

            insert_node_to_db(
                cursor, node_name, node_type, cpu, memory, disk, node_config
            )

        # 지금 보니까 Go로 작성된 버전은 마스터노드 검사하는게 없었네...
        if master_node_count == 0:
            logger.error("Kubernetes cluster must have at least one master node")
            connection.close()
            return 1

        master_nodes, worker_nodes = get_nodes_by_type(cursor)

        logger.log("🚀 Initializing cluster")
        if not create_vms(connection, cursor, master_nodes, worker_nodes,ubuntu_version):
            logger.error(
                "❌Failed to create instances for the cluster", context="Multipass"
            )
            connection.close()
            return 1

        setup_success = False
        if len(master_nodes) == 1:
            setup_success = setup_single_master_cluster(
                connection, cursor, master_nodes, worker_nodes, kubernetes_version
            )
            if not setup_success:
                logger.error("❌Failed to setup single master cluster")
        else:
            setup_success = setup_ha_master_cluster(
                connection, cursor, master_nodes, worker_nodes, kubernetes_version
            )
            if not setup_success:
                logger.error("❌Failed to setup HA master cluster")

        if not setup_success:
            connection.close()
            return 1

        master_name = next(iter(master_nodes.keys()))
        verify_cluster_status(master_name)

        logger.log("🔄 Adding k3s cluster to kubeconfig...")
        master_node_params = get_master_node_ips(connection, cursor, master_nodes)
        update_kubeconfig(master_node_params)

        logger.log(
            f"""
Cluster successfully initialized.

Master Node: {master_node_count}
Worker Node: {worker_node_count}
        """
        )

        connection.close()
        return 0

    except sqlite3.Error as e:
        logger.error(f"Error while working with database: {e}")
        return 1
    except Exception as e:
        logger.error(f"Programmatic Error: {e}")
        logger.error("Contact: hoplin.dev@gmail.com")
        return 1
