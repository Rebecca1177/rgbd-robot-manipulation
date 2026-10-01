"""Extracted unchanged from exercises/final_version.py: open_gripper, close_gripper."""

from src.config import GRIPPER_FORCE
from src.config import GRIPPER_OPEN_POSITION
from src.config import TIME_STEP
import pybullet as p
import time


def open_gripper(
    robot_id,
    finger_joint_indices,
    target_position=GRIPPER_OPEN_POSITION,
    force=GRIPPER_FORCE
):
    """
    打开 Panda 两个手指。
    """

    for joint_index in finger_joint_indices:
        p.setJointMotorControl2(
            robot_id,
            joint_index,
            p.POSITION_CONTROL,
            targetPosition=target_position,
            force=force
        )

    for _ in range(120):
        p.stepSimulation()
        time.sleep(TIME_STEP)


def close_gripper(
    robot_id,
    finger_joint_indices,
    target_position=0.0,
    force=GRIPPER_FORCE
):
    """
    闭合 Panda 两个手指。
    """

    for joint_index in finger_joint_indices:
        p.setJointMotorControl2(
            robot_id,
            joint_index,
            p.POSITION_CONTROL,
            targetPosition=target_position,
            force=force
        )

    for _ in range(240):
        p.stepSimulation()
        time.sleep(TIME_STEP)
