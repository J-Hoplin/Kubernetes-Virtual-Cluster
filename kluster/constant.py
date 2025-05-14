import os


CLUSTER_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CLUSTER_PATH)
SQLITE_PATH = os.path.join(CLUSTER_PATH, "database.db")
SCRIPTS_PATH = os.path.join(CLUSTER_PATH, "scripts")
# 나중에 한번에 변수명 바꾸자... 지금은 귀찮다... Default config path 대신 Cluster Config Path로 변경해야함
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "cluster-config.json")
