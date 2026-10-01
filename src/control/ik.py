"""Extracted unchanged from exercises/final_version.py: check_ik_candidate, solve_ik_with_seeds."""

import numpy as np
import pybullet as p


def check_ik_candidate(
    robot_id,
    hand_link_index,
    ik_solution,
    target_position,
    position_tolerance=1e-3
):
    """
    检查 IK 解是否满足：
    1. 前 7 个机械臂关节在 joint limits 内
    2. FK 后末端位置足够接近目标位置
    """

    q_candidate = np.array(
        ik_solution[:7]
    )

    # 保存当前真实状态
    original_q = np.array([
        p.getJointState(robot_id, i)[0]
        for i in range(7)
    ])

    # 1. Joint-limit check
    for joint_index in range(7):
        joint_info = p.getJointInfo(
            robot_id,
            joint_index
        )

        lower_limit = joint_info[8]
        upper_limit = joint_info[9]

        q = q_candidate[joint_index]

        if q < lower_limit or q > upper_limit:
            return False

    # 2. 临时放到 candidate，做 FK 验证
    for joint_index in range(7):
        p.resetJointState(
            robot_id,
            joint_index,
            q_candidate[joint_index]
        )

    hand_state = p.getLinkState(
        robot_id,
        hand_link_index
    )

    actual_position = np.array(
        hand_state[4]
    )

    position_error = np.linalg.norm(
        actual_position
        - np.array(target_position)
    )

    # 恢复原状态
    for joint_index in range(7):
        p.resetJointState(
            robot_id,
            joint_index,
            original_q[joint_index]
        )

    return position_error <= position_tolerance


def solve_ik_with_seeds(
    robot_id,
    hand_link_index,
    target_position,
    target_orientation,
    seed_configs
):
    """
    使用多组 seed 搜索 IK，
    返回第一个通过验证的合法解。
    """

    original_q = np.array([
        p.getJointState(robot_id, i)[0]
        for i in range(7)
    ])

    for seed in seed_configs:

        for joint_index in range(7):
            p.resetJointState(
                robot_id,
                joint_index,
                seed[joint_index]
            )

        ik_solution = p.calculateInverseKinematics(
            robot_id,
            hand_link_index,
            targetPosition=target_position,
            targetOrientation=target_orientation,
            maxNumIterations=1000,
            residualThreshold=1e-6
        )

        is_valid = check_ik_candidate(
            robot_id,
            hand_link_index,
            ik_solution,
            target_position
        )

        if is_valid:
            valid_solution = np.array(
                ik_solution[:7]
            )

            for joint_index in range(7):
                p.resetJointState(
                    robot_id,
                    joint_index,
                    original_q[joint_index]
                )

            return valid_solution

    for joint_index in range(7):
        p.resetJointState(
            robot_id,
            joint_index,
            original_q[joint_index]
        )

    return None
