"""Extracted unchanged from exercises/final_version.py: evaluate_trial."""

import numpy as np
import pybullet as p


def evaluate_trial(
    object_id,
    true_object_position,
    true_object_yaw,
    object_center_est,
    estimated_yaw,
    success_height=0.08
):
    """
    评估一次抓取实验。

    Ground truth 只用于 evaluation，
    不参与 perception / planning。

    Returns:
        success
        position_error_mm
        yaw_error_deg
        object_height
    """

    # -------------------------
    # 1. Perception position error
    # -------------------------

    position_error = np.linalg.norm(
        object_center_est
        - true_object_position
    )

    position_error_mm = (
        position_error * 1000
    )

    # -------------------------
    # 2. Yaw error
    # PCA axis has 180-degree ambiguity
    # -------------------------

    yaw_error = (
        estimated_yaw
        - true_object_yaw
        + np.pi / 2
    ) % np.pi - np.pi / 2

    yaw_error_deg = abs(
        np.rad2deg(yaw_error)
    )

    # -------------------------
    # 3. Grasp success
    # -------------------------

    object_position_after, _ = (
        p.getBasePositionAndOrientation(
            object_id
        )
    )

    object_height = (
        object_position_after[2]
    )

    success = (
        object_height >= success_height
    )

    return (
        success,
        position_error_mm,
        yaw_error_deg,
        object_height
    )
