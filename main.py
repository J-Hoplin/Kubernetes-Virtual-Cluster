import sys
import argparse

version = "2.0.0"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cluster base command",
        prog="cluster"
    )

    parser.add_argument(
        "--version",
    )


    ...