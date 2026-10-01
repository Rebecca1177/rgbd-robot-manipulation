"""Extracted unchanged from exercises/final_version.py: capture_rgbd."""

from src.config import CAMERA_FAR
from src.config import CAMERA_FOV
from src.config import CAMERA_NEAR
from src.config import DEPTH_DROPOUT_RATE
from src.config import DEPTH_NOISE_STD
from src.config import IMAGE_HEIGHT
from src.config import IMAGE_WIDTH
import numpy as np
import pybullet as p


def capture_rgbd(
    camera_eye,
    camera_target
):
    """
    从指定固定相机视角采集一帧 RGB-D。
    """

    view_matrix = p.computeViewMatrix(
        cameraEyePosition=camera_eye,
        cameraTargetPosition=camera_target,
        cameraUpVector=[0, 0, 1]
    )

    projection_matrix = p.computeProjectionMatrixFOV(
        fov=CAMERA_FOV,
        aspect=IMAGE_WIDTH / IMAGE_HEIGHT,
        nearVal=CAMERA_NEAR,
        farVal=CAMERA_FAR
    )

    image = p.getCameraImage(
        IMAGE_WIDTH,
        IMAGE_HEIGHT,
        viewMatrix=view_matrix,
        projectionMatrix=projection_matrix
    )

    rgba = np.array(
        image[2]
    ).reshape(
        IMAGE_HEIGHT,
        IMAGE_WIDTH,
        4
    )

    depth_buffer = np.array(
        image[3]
    ).reshape(
        IMAGE_HEIGHT,
        IMAGE_WIDTH
    )

    depth = (
        CAMERA_FAR * CAMERA_NEAR
        / (
            CAMERA_FAR
            - (
                CAMERA_FAR
                - CAMERA_NEAR
            ) * depth_buffer
        )
    )

    noise = np.random.normal(
        loc=0.0,
        scale=DEPTH_NOISE_STD,
        size=depth.shape
    )

    depth_noisy = depth + noise

    dropout_mask = (
        np.random.random(depth.shape)
        < DEPTH_DROPOUT_RATE
    )

    depth_noisy[dropout_mask] = CAMERA_FAR

    return rgba, depth_noisy
