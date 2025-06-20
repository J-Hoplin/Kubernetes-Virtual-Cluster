import argparse
from kluster.command.actions import init, destroy, shell, doctor, config, view


def action_parser(parser: argparse.ArgumentParser):
    action_parser = parser.add_subparsers(
        title="Cluster action command", dest="action", help="Cluster of action"
    )
    action_parser.required = True

    # Configuration for sub command - init
    init_action = action_parser.add_parser("init", help="Initialize Cluster")
    init_action.add_argument(
        "--config",
        "-c",
        help="Configuration file path. Default is './cluster-config.json' in command executed path",
        default="cluster-config.json",
    )
    # https://docs.python.org/ko/3.13/library/argparse.html#action
    init_action.add_argument(
        "--force",
        "-f",
        help="Force initialize cluster. Previous cluster states will be lost and no more managed",
        action="store_true",
    )
    init_action.set_defaults(func=init.run)

    # Configuration for sub command - config
    config_parser = action_parser.add_parser("config", help="Manage cluster configuration")
    config_subparsers = config_parser.add_subparsers(
        title="Config actions", dest="config_action", help="Configuration actions"
    )
    config_subparsers.required = True
    # Subcommand for sub command - kluster config
    edit_parser = config_subparsers.add_parser("edit", help="Edit cluster configuration")
    edit_parser.set_defaults(func=config.edit)

    # Configuration for sub command - destroy
    destroy_parser = action_parser.add_parser("destroy", help="Destroy the cluster")
    destroy_parser.add_argument(
        "-f", "--force", help="Force deletion without confirmation", action="store_true"
    )
    destroy_parser.set_defaults(func=destroy.run)

    # Configuration for sub command - shell
    shell_parser = action_parser.add_parser("shell", help="Access shell of a node")
    shell_parser.add_argument("node", help="Node name to access")
    shell_parser.set_defaults(func=shell.run)

    # Configuration for sub command - doctor
    doctor_parser = action_parser.add_parser("doctor", help="Check dependencies")
    doctor_parser.set_defaults(func=doctor.run)

    # Configuration for sub command - view
    view_parser = action_parser.add_parser("view", help="View cluster state")
    view_parser.set_defaults(func=view.run)
