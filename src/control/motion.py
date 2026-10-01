"""Extracted unchanged from exercises/final_version.py: move_to_joint_target, execute_cartesian_move."""

from src.config import CARTESIAN_WAYPOINTS
from src.config import JOINT_TRAJECTORY_STEPS
from src.config import TIME_STEP
import numpy as np
import pybullet as p
import time


def move_to_joint_target(
    robot_id,
    target_q,
    num_steps=JOINT_TRAJECTORY_STEPS
):
    """
    从当前关节状态平滑移动到目标关节构型。
    """

    current_q = np.array([
        p.getJointState(robot_id, i)[0]
        for i in range(7)
    ])

    trajectory = np.linspace(
        current_q,
        target_q,
        num_steps
    )

    for q_target in trajectory:

        for joint_index in range(7):
            p.setJointMotorControl2(
                robot_id,
                joint_index,
                p.POSITION_CONTROL,
                targetPosition=q_target[joint_index]
            )

        p.stepSimulation()
        time.sleep(TIME_STEP)


def execute_cartesian_move(
    robot_id,
    hand_link_index,
    start_position,
    target_position,
    target_orientation,
    num_waypoints=CARTESIAN_WAYPOINTS
):
    """
    通过一系列 Cartesian waypoints，
    让末端近似沿直线移动到目标位置。
    """

    waypoints = np.linspace(
        start_position,
        target_position,
        num_waypoints
    )

    for waypoint in waypoints:

        ik_solution = p.calculateInverseKinematics(
            robot_id,
            hand_link_index,
            targetPosition=waypoint,
            targetOrientation=target_orientation,
            maxNumIterations=1000,
            residualThreshold=1e-6
        )

        for joint_index in range(7):
            p.setJointMotorControl2(
                robot_id,
                joint_index,
                p.POSITION_CONTROL,
                targetPosition=ik_solution[joint_index]
            )

        for _ in range(8):
            p.stepSimulation()
            time.sleep(TIME_STEP)
