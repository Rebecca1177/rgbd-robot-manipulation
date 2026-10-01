"""Extracted unchanged from exercises/final_version.py: depth_to_pointcloud, pointcloud_camera_to_world."""

from src.config import CAMERA_FOV
from src.config import IMAGE_HEIGHT
from src.config import IMAGE_WIDTH
import numpy as np


def depth_to_pointcloud(depth):
    """
    将深度图转换为相机坐标系下的 N×3 点云。
    """

    fy = (
        IMAGE_HEIGHT / 2
        / np.tan(
            np.deg2rad(CAMERA_FOV) / 2
        )
    )

    fx = fy

    cx = IMAGE_WIDTH / 2
    cy = IMAGE_HEIGHT / 2

    u, v = np.meshgrid(
        np.arange(IMAGE_WIDTH),
        np.arange(IMAGE_HEIGHT)
    )

    z = depth

    x = (
        (u - cx)
        * z
        / fx
    )

    y = (
        (v - cy)
        * z
        / fy
    )

    points = np.stack(
        [x, y, z],
        axis=-1
    )

    return points.reshape(-1, 3)


def pointcloud_camera_to_world(
    points_cam,
    camera_eye,
    camera_target
):
    """
    将相机坐标系点云转换到 world frame。
    """

    camera_eye = np.array(
        camera_eye,
        dtype=float
    )

    camera_target = np.array(
        camera_target,
        dtype=float
    )

    camera_up = np.array(
        [0.0, 0.0, 1.0]
    )

    # Camera Z: forward
    z_axis = (
        camera_target
        - camera_eye
    )

    z_axis = (
        z_axis
        / np.linalg.norm(z_axis)
    )

    # Camera X: right
    x_axis = np.cross(
        z_axis,
        camera_up
    )

    x_axis = (
        x_axis
        / np.linalg.norm(x_axis)
    )

    # Camera Y: down
    y_axis = np.cross(
        z_axis,
        x_axis
    )

    y_axis = (
        y_axis
        / np.linalg.norm(y_axis)
    )

    R_world_camera = np.column_stack([
        x_axis,
        y_axis,
        z_axis
    ])

    points_world = (
        points_cam
        @ R_world_camera.T
        + camera_eye
    )

    return points_world
