"""Repeat the seed-42 five-trial DIRECT comparison against the historical file."""

import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=root / "exercises/final_version.py")
    parser.add_argument("--output-dir", type=Path, default=root / "results/regression")
    parser.add_argument("--baseline-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    original = args.original.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    if args.baseline_worker:
        import numpy as np
        import open3d as o3d
        import pybullet as p

        tree = ast.parse(original.read_text(encoding="utf-8-sig"))
        block = next(n for n in tree.body if isinstance(n, ast.If))
        connection = block.body[0].value
        assert ast.unparse(connection) == "p.connect(p.GUI)"
        connection.args[0].attr = "DIRECT"
        np.random.seed(42)
        o3d.utility.random.seed(42)
        namespace = {"__name__": "__main__"}
        try:
            exec(compile(ast.fix_missing_locations(tree), str(original), "exec"), namespace)
            summary = {
                "results": namespace["results"],
                "success_rate": namespace["success_rate"],
                "mean_position_error_mm": namespace["mean_position_error"],
                "mean_yaw_error_deg": namespace["mean_yaw_error"],
            }
            (output / "baseline_seed42.json").write_text(
                json.dumps(summary, indent=2, default=lambda value: value.item()), encoding="utf-8"
            )
        finally:
            if p.isConnected():
                p.disconnect()
        return

    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    commands = [
        ("source_check", [root / "tests/check_refactor.py", "--original", original]),
        ("baseline_seed42", [Path(__file__).resolve(), "--original", original, "--output-dir", output, "--baseline-worker"]),
        ("refactored_seed42", [root / "scripts/run_benchmark.py", "--trials", "5", "--seed", "42", "--output", output / "refactored_seed42.json"]),
        ("comparison", [root / "tests/check_refactor.py", "--original", original, "--old-results", output / "baseline_seed42.json", "--new-results", output / "refactored_seed42.json"]),
    ]
    for name, command in commands:
        print(f"Running {name}...", flush=True)
        with (output / f"{name}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run([sys.executable, "-B", "-u", *map(str, command)], cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        print((output / f"{name}.log").read_text(encoding="utf-8"), flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
