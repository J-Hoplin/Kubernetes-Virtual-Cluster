import os
import sqlite3
import subprocess
from cluster.utils import logger
from cluster.constant import SQLITE_PATH


def check_node_exists(node_name, cursor):
    cursor.execute("SELECT node_type FROM nodes WHERE name = ?", (node_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def run(args):
    if not os.path.exists(SQLITE_PATH):
        logger.error("No cluster state found")
        return 1

    try:
        with sqlite3.connect(SQLITE_PATH) as connection:
            cursor = connection.cursor()

            node_type = check_node_exists(args.node, cursor)

            if not node_type:
                logger.error(f"❌ Instance'{args.node}' not found")
                return 1

            logger.log(f"🔄 Connecting to {node_type} node: {args.node}")

            try:
                subprocess.run(["multipass", "shell", args.node], check=True)
                return 0
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to connect to node: {e}")
                return 1

    except sqlite3.Error as e:
        logger.error(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Programmatic error: {e}")
        return 1
