import sys
import subprocess
import json
from kluster.utils import logger


def check_and_download_image(ubuntu_version):
    """
    1. Multipass에서 명시된 ubuntu 버전 이미지를 지원하는지 확인
    2. 이미지가 없는 경우 다운로드
    3. 이미지 버전은 설치된 multipass에서 지원하는 버전을 따라야함
    """
    image_name = f"{ubuntu_version}"
    log_context = "Multipass"

    try:
        result = subprocess.run(
            ["multipass", "find"], capture_output=True, text=True, check=True
        )
        available_images = result.stdout

        if image_name in available_images:
            logger.log(
                f"Ubuntu {image_name} is already available in host machine",
                context=log_context,
            )
            return image_name

        logger.log(
            f"Ubuntu {image_name} not found. Attempting to download...",
            context=log_context,
        )
        subprocess.run(["multipass", "find", image_name], check=True)
        logger.log(f"Ubuntu {image_name} prepared!", context=log_context)

    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error: Unable to find or download Ubuntu {ubuntu_version} image."
        )
        logger.error(f"Error details: {e}")
        sys.exit(1)


def create_vms(connection, cursor, master_nodes, worker_nodes,ubuntu_version):
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
            ubuntu_version
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
