import os
import sqlite3
from kluster.utils import logger
from kluster.constant import SQLITE_PATH
from kluster.utils.dependency import require_dependencies


def format_node_info(nodes):
    headers = ["ID", "Type", "CPU", "Memory(MB)", "Disk(GB)", "IP(Internal)", "Created At"]
    widths = [4, 8, 5, 11, 9, 15, 30]
    
    header = "  ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
    separator = "-" * len(header)
    
    rows = []
    for node in nodes:
        row = "  ".join(f"{str(field):<{w}}" for field, w in zip(node, widths))
        rows.append(row)
    
    return f"\n{header}\n{separator}\n" + "\n".join(rows)


@require_dependencies()
def run(args):
    if not os.path.exists(SQLITE_PATH):
        logger.error("No cluster state found")
        return 1

    try:
        with sqlite3.connect(SQLITE_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, node_type, cpu, memory, disk, ip, created_at 
                FROM nodes 
                ORDER BY node_type DESC, id ASC
            """)
            nodes = cursor.fetchall()

            if not nodes:
                logger.error("❌ No nodes found in cluster state")
                return 1

            formatted_output = format_node_info(nodes)
            logger.log(formatted_output)
            return 0

    except sqlite3.Error as e:
        logger.error("❌ No nodes found in cluster state")
        return 1
    except Exception as e:
        logger.error(f"❌ Programmatic error: {e}")
        return 1 