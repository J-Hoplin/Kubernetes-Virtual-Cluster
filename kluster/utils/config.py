import os
import json
from kluster.constant import DEFAULT_CONFIG_PATH


"""
필요한 경우

cluster-config.json파일이 유실되거나 고의적으로 삭제되었을때
기본 파일로 대체하기 위함임.
"""
def create_default_config():
    default_config = {
        "k3s_version": "v1.26.6+k3s1",
        "ubuntu_version": "22.04",
        "nodes": {
            "master-1": {
                "type": "master",
                "cpu": 2,
                "memory": 2048,
                "disk": 10,
                "ip": ""
            }
        }
    }
    
    os.makedirs(os.path.dirname(DEFAULT_CONFIG_PATH), exist_ok=True)
    
    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    return default_config