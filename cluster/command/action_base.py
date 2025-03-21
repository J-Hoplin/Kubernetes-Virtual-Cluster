import argparse
from cluster.command.actions import init

def action_parser(parser: argparse.ArgumentParser):
    action_parser = parser.add_subparsers(
        title="Cluster action command",
        dest="action",
        help="Cluster of action"
    )
    action_parser.required = True

    # Configuration for sub command - Init
    init_action = action_parser.add_parser("init", help="Initialize Cluster")
    init_action.add_argument(
        "--config",
        "-c",
        help="Configuration file path. Default is './cluster-config.yaml' in command executed path",
        default="./cluster-config.yaml"
    )
    # https://docs.python.org/ko/3.13/library/argparse.html#action
    init_action.add_argument(
        "--force",
        "-f",
        help="Force initialize cluster. Previous cluster states will be lost and no more managed",
        action="store_true"
    )
    init_action.set_defaults(func=init.run)

