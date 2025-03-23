import os
import sqlite3
from cluster.utils import logger
from cluster.constant import SQLITE_PATH
from cluster.command.actions.destroy_kubeconfig import cleanup_kubeconfig
from cluster.command.actions.destroy_multipass import destroy_node, purge_multipass


def run(args):
    if not os.path.exists(SQLITE_PATH):
        logger.error("No cluster state found")
        return 1

    try:
        with sqlite3.connect(SQLITE_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT name, node_type FROM nodes")
            nodes = cursor.fetchall()

            if not nodes:
                logger.error("❌ No nodes found in cluster state")
                return 1

            total_nodes = len(nodes)
            master_nodes = sum(1 for _, node_type in nodes if node_type == "master")
            worker_nodes = total_nodes - master_nodes

            logger.log(f"👀 Found: {total_nodes} nodes ({master_nodes} masters, {worker_nodes} workers)")

            if not args.force:
                confirmation = input("⚠️ Do you want to delete the cluster? (Y/N): ")
                if confirmation.lower() != "y":
                    logger.warn("Deletion cancelled")
                    return 0

            for node_name, node_type in nodes:
                logger.log(f"🔄 Deleting {node_type} node: {node_name}")
                if destroy_node(node_name):
                    logger.log(f"✅ Node {node_name} destroyed")
                else:
                    logger.warn(f"❌ Failed to destroy node {node_name}")

            if purge_multipass():
                logger.log("✅ Purged all destroyed instances")
            else:
                logger.warn("❌ Failed to purge destroyed instances")

            if cleanup_kubeconfig(nodes):
                logger.log("✅ Cleaned up kubeconfig")
            else:
                logger.warn("❌ Failed to clean up some kubeconfig entries")

            cursor.execute("DROP TABLE IF EXISTS nodes")
            connection.commit()
            logger.log("✅ Cleaned up cluster state database")
            return 0

    except sqlite3.Error as e:
        logger.error(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Programmatic error: {e}")
        return 1
