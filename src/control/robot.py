"""Extracted unchanged from exercises/final_version.py: find_robot_links."""

import pybullet as p


def find_robot_links(robot_id):
    """
    查找 Panda hand link 和两个 finger joints。

    Returns:
        hand_link_index
        finger_joint_indices
    """

    hand_link_index = None
    finger_joint_indices = []

    for joint_index in range(
        p.getNumJoints(robot_id)
    ):
        joint_info = p.getJointInfo(
            robot_id,
            joint_index
        )

        joint_name = joint_info[1].decode("utf-8")
        link_name = joint_info[12].decode("utf-8")

        if link_name == "panda_hand":
            hand_link_index = joint_index

        if "finger_joint" in joint_name:
            finger_joint_indices.append(
                joint_index
            )

    return (
        hand_link_index,
        finger_joint_indices
    )
