"""Extracted unchanged from exercises/final_version.py: run_trial."""

from src.config import IK_SEED_CONFIGS
from src.config import LIFT_DISTANCE
from src.planning.grasp import build_grasp_pose
from src.control.gripper import close_gripper
from src.evaluation.metrics import evaluate_trial
from src.control.motion import execute_cartesian_move
from src.control.robot import find_robot_links
from src.control.motion import move_to_joint_target
import numpy as np
from src.control.gripper import open_gripper
from src.perception.segmentation import perceive_object
from src.simulation.scene import setup_scene
from src.control.ik import solve_ik_with_seeds


def run_trial():
    """
    运行一次完整的随机抓取实验。

    Returns:
        result: dict
    """

    # 1. Scene setup
    robot_id, object_id, true_object_position, true_object_yaw = setup_scene()

    # 2. Robot structure
    hand_link_index, finger_joint_indices = find_robot_links(robot_id)

    # 3. Perception
    object_center_est, estimated_yaw = perceive_object()

    # 4. Grasp planning
    (
        grasp_position,
        grasp_quat,
        hand_target_position,
        pregrasp_position,
        pregrasp_quat
    ) = build_grasp_pose(
        object_center_est,
        estimated_yaw
    )

    # 5. Pre-grasp IK
    pregrasp_ik = solve_ik_with_seeds(
        robot_id,
        hand_link_index,
        pregrasp_position,
        pregrasp_quat,
        IK_SEED_CONFIGS
    )

    # 如果没有找到合法 IK，这次 trial 直接判失败
    if pregrasp_ik is None:
        position_error = np.linalg.norm(
            object_center_est - true_object_position
        ) * 1000

        yaw_error = (
            estimated_yaw
            - true_object_yaw
            + np.pi / 2
        ) % np.pi - np.pi / 2

        return {
            "success": False,
            "failure_reason": "ik_failed",
            "position_error_mm": position_error,
            "yaw_error_deg": abs(np.rad2deg(yaw_error)),
            "object_height": None
        }

    # 6. Move to pre-grasp
    move_to_joint_target(
        robot_id,
        pregrasp_ik
    )

    # 7. Open gripper
    open_gripper(
        robot_id,
        finger_joint_indices
    )

    # 8. Cartesian approach
    execute_cartesian_move(
        robot_id,
        hand_link_index,
        pregrasp_position,
        hand_target_position,
        grasp_quat
    )

    # 9. Close gripper
    close_gripper(
        robot_id,
        finger_joint_indices
    )

    # 10. Lift
    lift_target_position = (
        hand_target_position
        + np.array([0.0, 0.0, LIFT_DISTANCE])
    )

    execute_cartesian_move(
        robot_id,
        hand_link_index,
        hand_target_position,
        lift_target_position,
        grasp_quat
    )

    # 11. Evaluation
    (
        success,
        position_error_mm,
        yaw_error_deg,
        object_height
    ) = evaluate_trial(
        object_id,
        true_object_position,
        true_object_yaw,
        object_center_est,
        estimated_yaw
    )

    result = {
        "success": success,
        "failure_reason": None if success else "grasp_failed",
        "position_error_mm": position_error_mm,
        "yaw_error_deg": yaw_error_deg,
        "object_height": object_height
    }

    return result
