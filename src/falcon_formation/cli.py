"""
Command Line Interface for Falcon Formation.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import argparse
import time

from falcon_formation.main import falcon_formation


def main() -> int:
    """Main function of the Falcon Formation application."""
    parser = argparse.ArgumentParser(description="Falcon Formation CLI")
    parser.add_argument("team", type=str, help="Name of the team")
    args = parser.parse_args()

    start_time = time.time()

    print(falcon_formation(args.team))  # noqa: T201

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds.")  # noqa: T201

    return 0
