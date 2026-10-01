"""Run one GUI grasp demonstration."""

from pathlib import Path
import sys

# Support running this script from any current working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import numpy as np
from src.simulation.runtime import connect_simulation, disconnect_simulation


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Unsupported JSON value: {type(value)}")


def main():
    from src.pipeline import run_trial

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--no-wait", action="store_true", help="Close immediately after evaluation")
    args = parser.parse_args()
    client = connect_simulation(gui=True, seed=args.seed)
    try:
        result = run_trial()
        print(json.dumps(result, indent=2, default=json_default))
        if not args.no_wait:
            input("Press Enter to close the simulation...")
    finally:
        disconnect_simulation(client)


if __name__ == "__main__":
    main()
