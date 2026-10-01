"""Batch benchmark; DIRECT by default, GUI with --gui."""

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
    from src.evaluation.benchmark import run_benchmark

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--output", type=Path, help="Save per-trial results and summary as JSON")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    client = connect_simulation(gui=args.gui, seed=args.seed)
    try:
        summary = run_benchmark(args.trials)
    finally:
        disconnect_simulation(client)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2, default=json_default), encoding="utf-8")


if __name__ == "__main__":
    main()
