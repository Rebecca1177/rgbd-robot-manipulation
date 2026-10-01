"""Extracted unchanged from exercises/final_version.py: build_grasp_pose."""

from src.config import HAND_TO_GRASP_OFFSET
from src.config import PREGRASP_DISTANCE
import numpy as np
import pybullet as p


def build_grasp_pose(
    object_center_est,
    estimated_yaw
):
    """
    根据视觉估计的物体中心和 yaw，
    生成 grasp pose、hand target 和 pre-grasp pose。

    Returns:
        grasp_position
        grasp_quat
        hand_target_position
        pregrasp_position
        pregrasp_quat
    """

    # 1. Grasp center
    grasp_position = object_center_est.copy()

    # 2. Grasp orientation
    grasp_quat = p.getQuaternionFromEuler([
        np.pi,
        0.0,
        estimated_yaw
    ])

    # 3. Quaternion -> rotation matrix
    grasp_rot = np.array(
        p.getMatrixFromQuaternion(
            grasp_quat
        )
    ).reshape(3, 3)

    # 4. panda_hand -> grasp center offset
    hand_offset = np.array([
        0.0,
        0.0,
        HAND_TO_GRASP_OFFSET
    ])

    hand_target_position = (
        grasp_position
        - grasp_rot @ hand_offset
    )

    # 5. Pre-grasp: move backward along hand Z axis
    hand_z_axis = grasp_rot[:, 2]

    pregrasp_position = (
        hand_target_position
        - hand_z_axis * PREGRASP_DISTANCE
    )

    pregrasp_quat = grasp_quat

    return (
        grasp_position,
        grasp_quat,
        hand_target_position,
        pregrasp_position,
        pregrasp_quat
    )
