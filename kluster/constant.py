import os


CLUSTER_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CLUSTER_PATH)
SQLITE_PATH = os.path.join(CLUSTER_PATH, "database.db")
SCRIPTS_PATH = os.path.join(CLUSTER_PATH, "scripts")
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "cluster-config.json")
