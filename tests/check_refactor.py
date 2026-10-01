"""Verify function/config preservation and compare saved real benchmark runs."""

import argparse
import ast
import json
from pathlib import Path


def check_source(original, root):
    old = ast.parse(original.read_text(encoding="utf-8-sig"))
    expected = {n.name: ast.dump(n) for n in old.body if isinstance(n, ast.FunctionDef)}
    found = {}
    for path in (root / "src").rglob("*.py"):
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.FunctionDef) and node.name in expected:
                assert node.name not in found, f"Duplicate function: {node.name}"
                found[node.name] = ast.dump(node)
    assert found == expected, "Missing or changed original functions"
    assignments = lambda tree: [ast.dump(n) for n in tree.body if isinstance(n, ast.Assign)]
    assert assignments(old) == assignments(ast.parse((root / "src/config.py").read_text(encoding="utf-8")))
    old_main = next(n for n in old.body if isinstance(n, ast.If))
    benchmark = ast.parse((root / "src/evaluation/benchmark.py").read_text(encoding="utf-8"))
    new_main = next(n for n in benchmark.body if isinstance(n, ast.FunctionDef))
    assert [ast.dump(n) for n in old_main.body[3:]] == [ast.dump(n) for n in new_main.body[3:-1]]
    print(f"PASS: {len(expected)} function bodies/signatures, all constants, benchmark loop/statistics unchanged")


def check_results(old_path, new_path):
    old = json.loads(old_path.read_text(encoding="utf-8"))
    new = json.loads(new_path.read_text(encoding="utf-8"))
    assert len(old["results"]) == len(new["results"])
    max_delta = 0.0
    for before, after in zip(old["results"], new["results"]):
        assert before.keys() == after.keys()
        for key in before:
            if isinstance(before[key], (bool, str)) or before[key] is None:
                assert before[key] == after[key], (key, before[key], after[key])
            else:
                delta = abs(before[key] - after[key])
                max_delta = max(max_delta, delta)
                assert delta <= 1e-9, (key, delta)
    for key in ["success_rate", "mean_position_error_mm", "mean_yaw_error_deg"]:
        assert abs(old[key] - new[key]) <= 1e-9, key
    print(f"PASS: {len(old['results'])} trial results and aggregate metrics match; maximum trial numeric difference={max_delta}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--old-results", type=Path)
    parser.add_argument("--new-results", type=Path)
    args = parser.parse_args()
    check_source(args.original, Path(__file__).resolve().parents[1])
    if args.old_results and args.new_results:
        check_results(args.old_results, args.new_results)
