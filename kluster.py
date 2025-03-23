#!/usr/bin/env python3

import sys
import argparse
from kluster.command.action_base import action_parser

version = "2.0.0"


def parser_bootstrap():
    parser = argparse.ArgumentParser(description="Cluster base command", prog="kluster")
    parser.add_argument("--version", "-v", action="version", version=version)
    action_parser(parser)
    return parser


def main():
    parser = parser_bootstrap()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
