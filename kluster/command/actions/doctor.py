from kluster.utils.dependency import require_dependencies


@require_dependencies(is_doctor=True)
def run(args):
    return 0
