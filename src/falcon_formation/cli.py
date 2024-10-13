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

    parser.add_argument(
        "team",
        type=str,
        help="Name of the team",
    )
    parser.add_argument(
        "--goalie",
        action="store_true",
        help="Whether to only check for goalies",
    )
    args = parser.parse_args()

    if args.goalie:
        output, _ = falcon_formation(args.team, goalie=True)
        print(output)  # noqa: T201
        return 0

    start_time = time.time()
    output, output_metadata = falcon_formation(args.team)
    print(output)  # noqa: T201
    # !This separator is used in the GitHub Actions to send multiple messages.
    print("\n---\n")  # noqa: T201
    end_time = time.time()

    output_metadata += f"\n\nExecution time: {end_time - start_time:.2f} seconds."
    print(output_metadata)  # noqa: T201

    return 0
