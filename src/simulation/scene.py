"""Extracted unchanged from exercises/final_version.py: setup_scene."""

from src.config import GUI_CAMERA_DISTANCE
from src.config import GUI_CAMERA_PITCH
from src.config import GUI_CAMERA_TARGET
from src.config import GUI_CAMERA_YAW
from src.config import OBJECT_HEIGHT_RANGE
from src.config import OBJECT_LENGTH_RANGE
from src.config import OBJECT_MASS
from src.config import OBJECT_WIDTH_RANGE
from src.config import TIME_STEP
from src.config import WORKSPACE_X_RANGE
from src.config import WORKSPACE_Y_RANGE
import numpy as np
import pybullet as p
import pybullet_data


def setup_scene():
    """
    创建一次实验场景。

    Returns:
        robot_id
        object_id
        true_object_position
        true_object_yaw
    """
    p.resetDebugVisualizerCamera(
        cameraDistance=GUI_CAMERA_DISTANCE,
        cameraYaw=GUI_CAMERA_YAW,
        cameraPitch=GUI_CAMERA_PITCH,
        cameraTargetPosition=GUI_CAMERA_TARGET
    )

    p.resetSimulation()

    p.setAdditionalSearchPath(
        pybullet_data.getDataPath()
    )

    p.setGravity(0, 0, -9.81)

    p.setTimeStep(TIME_STEP)

    p.loadURDF("plane.urdf")

    # Load Panda robot
    robot_id = p.loadURDF(
        "franka_panda/panda.urdf",
        useFixedBase=True
    )

    # Random object yaw
    true_object_yaw = np.random.uniform(
        -np.pi,
        np.pi
    )
    object_length = np.random.uniform(
        OBJECT_LENGTH_RANGE[0],
        OBJECT_LENGTH_RANGE[1]
    )

    object_width = np.random.uniform(
        OBJECT_WIDTH_RANGE[0],
        OBJECT_WIDTH_RANGE[1]
    )

    object_height = np.random.uniform(
        OBJECT_HEIGHT_RANGE[0],
        OBJECT_HEIGHT_RANGE[1]
    )
    # Compute yaw-dependent footprint
    half_x = (
        object_length / 2 * abs(np.cos(true_object_yaw))
        + object_width / 2 * abs(np.sin(true_object_yaw))
    )

    half_y = (
        object_length / 2 * abs(np.sin(true_object_yaw))
        + object_width / 2 * abs(np.cos(true_object_yaw))
    )

    # Random object position while keeping
    # the whole object inside the workspace
    object_x = np.random.uniform(
        WORKSPACE_X_RANGE[0] + half_x,
        WORKSPACE_X_RANGE[1] - half_x
    )

    object_y = np.random.uniform(
        WORKSPACE_Y_RANGE[0] + half_y,
        WORKSPACE_Y_RANGE[1] - half_y
    )

    true_object_position = np.array([
        object_x,
        object_y,
        object_height / 2
    ])

    object_orientation = p.getQuaternionFromEuler(
        [0.0, 0.0, true_object_yaw]
    )

    # 创建碰撞和视觉几何
    collision_shape = p.createCollisionShape(
        p.GEOM_BOX,
        halfExtents=[
            object_length / 2,
            object_width / 2,
            object_height / 2
        ]
    )

    visual_shape = p.createVisualShape(
        p.GEOM_BOX,
        halfExtents=[
            object_length / 2,
            object_width / 2,
            object_height / 2
        ]
    )

    # 创建刚体
    object_id = p.createMultiBody(
        baseMass=OBJECT_MASS,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=visual_shape,
        basePosition=true_object_position,
        baseOrientation=object_orientation
    )

    return (
        robot_id,
        object_id,
        true_object_position,
        true_object_yaw
    )
