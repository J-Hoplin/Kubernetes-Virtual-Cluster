import os
import subprocess
from kluster.constant import DEFAULT_CONFIG_PATH
from kluster.utils import logger
from kluster.utils.dependency import require_dependencies
from kluster.utils.config import create_default_config

@require_dependencies(dependencies=["vim"])
def edit(args):
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        logger.log(f"⚠️ Config file not found at {DEFAULT_CONFIG_PATH}")
        logger.log(f"🔄 Creating default configuration...")
        create_default_config()
    
    try:
        logger.log(f"🚀 Opening cluster config file")
        subprocess.run(["vim", DEFAULT_CONFIG_PATH])
        return 0
    except Exception as e:
        logger.error(f"❌ Error editing configuration: {e}")
        return 1