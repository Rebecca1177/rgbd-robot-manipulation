"""Original five-trial benchmark loop and summary statistics."""

import numpy as np
from src.pipeline import run_trial


def run_benchmark(num_trials=5):
    if num_trials < 1:
        raise ValueError("num_trials must be positive")
    NUM_TRIALS = num_trials
    results = []
    for trial_idx in range(NUM_TRIALS):
        print(f"Starting trial {trial_idx + 1}...")
        result = run_trial()
        results.append(result)

        print(
            f"Trial {trial_idx + 1}/{NUM_TRIALS}: "
            f"success={result['success']}, "
            f"position_error={result['position_error_mm']:.2f} mm, "
            f"yaw_error={result['yaw_error_deg']:.2f} deg"
        )

    success_rate = np.mean([
        result["success"]
        for result in results
    ])

    mean_position_error = np.mean([
        result["position_error_mm"]
        for result in results
    ])

    mean_yaw_error = np.mean([
        result["yaw_error_deg"]
        for result in results
    ])

    print("\n===== Benchmark Result =====")
    print(f"Success rate: {success_rate * 100:.1f}%")
    print(f"Mean position error: {mean_position_error:.2f} mm")
    print(f"Mean yaw error: {mean_yaw_error:.2f} deg")
    return {
        "results": results,
        "success_rate": float(success_rate),
        "mean_position_error_mm": float(mean_position_error),
        "mean_yaw_error_deg": float(mean_yaw_error),
    }
