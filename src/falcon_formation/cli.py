"""
Command Line Interface for Falcon Formation.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import time

from falcon_formation.main import falcon_formation


def main() -> int:
    """Main function of the Falcon Formation application."""
    start_time = time.time()

    print(falcon_formation())  # noqa: T201

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds.")  # noqa: T201

    return 0
