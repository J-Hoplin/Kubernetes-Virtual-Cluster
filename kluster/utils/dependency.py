import shutil
import functools
from kluster.utils import logger


def require_dependencies(is_doctor: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(args):
            if not _check_dependencies(is_doctor=is_doctor):
                return 1
            return func(args)

        return wrapper

    return decorator


def _check_dependencies(is_doctor: bool = False):
    required_tools = {"kubectl": True, "multipass": True, "helm": False}

    all_installed = True
    status_messages = []

    for tool, is_required in required_tools.items():
        is_installed = shutil.which(tool) is not None
        status = "✅" if is_installed else "❌"
        not_required = " (Not Required)" if not is_required else ""
        status_messages.append(f"{status} {tool}{not_required}")

        if is_required and not is_installed:
            all_installed = False

    if not all_installed or is_doctor:
        for message in status_messages:
            logger.log(message)
        return False

    return True
