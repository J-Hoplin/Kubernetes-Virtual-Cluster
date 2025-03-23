from kluster.utils.dependency import check_dependencies


def run(args):
    check_dependencies(is_doctor=True)
    return 0
