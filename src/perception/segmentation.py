"""Extracted unchanged from exercises/final_version.py: perceive_object."""

from src.config import CAMERA1_EYE
from src.config import CAMERA2_EYE
from src.config import CAMERA_FAR
from src.config import CLUSTER_MIN_MEAN_Z
from src.config import CLUSTER_MIN_POINTS
from src.config import GROUND_DISTANCE_THRESHOLD
from src.config import MIN_OBJECT_Z
from src.config import WORKSPACE_CENTER
from src.config import WORKSPACE_X_RANGE
from src.config import WORKSPACE_Y_RANGE
from src.perception.rgbd import capture_rgbd
from src.perception.pointcloud import depth_to_pointcloud
import numpy as np
import open3d as o3d
from src.perception.pointcloud import pointcloud_camera_to_world


def perceive_object():
    """
    使用双 RGB-D 相机估计目标物体点云。

    Returns:
        workspace_points
    """

    # -------------------------
    # 1. Capture dual RGB-D
    # -------------------------

    rgba1, depth1 = capture_rgbd(
        CAMERA1_EYE,
        WORKSPACE_CENTER
    )

    rgba2, depth2 = capture_rgbd(
        CAMERA2_EYE,
        WORKSPACE_CENTER
    )

    # -------------------------
    # 2. Depth -> camera-frame point clouds
    # -------------------------

    points_cam1 = depth_to_pointcloud(
        depth1
    )

    points_cam2 = depth_to_pointcloud(
        depth2
    )

    # -------------------------
    # 3. Camera frame -> world frame
    # -------------------------

    points_world1 = pointcloud_camera_to_world(
        points_cam1,
        CAMERA1_EYE,
        WORKSPACE_CENTER
    )

    points_world2 = pointcloud_camera_to_world(
        points_cam2,
        CAMERA2_EYE,
        WORKSPACE_CENTER
    )

    # -------------------------
    # 4. Remove far-plane points
    # -------------------------

    valid1 = (
        depth1.reshape(-1)
        < CAMERA_FAR - 0.01
    )

    valid2 = (
        depth2.reshape(-1)
        < CAMERA_FAR - 0.01
    )

    points_world1 = points_world1[
        valid1
    ]

    points_world2 = points_world2[
        valid2
    ]

    # -------------------------
    # 5. Fuse point clouds
    # -------------------------

    points_fused = np.vstack([
        points_world1,
        points_world2
    ])

    pcd_fused = o3d.geometry.PointCloud()

    pcd_fused.points = (
        o3d.utility.Vector3dVector(
            points_fused
        )
    )

    # -------------------------
    # 6. Ground removal
    # -------------------------

    _, inliers = pcd_fused.segment_plane(
        distance_threshold=GROUND_DISTANCE_THRESHOLD,
        ransac_n=3,
        num_iterations=1000
    )

    non_ground_cloud = (
        pcd_fused.select_by_index(
            inliers,
            invert=True
        )
    )

    non_ground_points = np.asarray(
        non_ground_cloud.points
    )


    # -------------------------
    # 7. Workspace crop
    # -------------------------

    workspace_mask = (
        (non_ground_points[:, 0] >= WORKSPACE_X_RANGE[0])
        & (non_ground_points[:, 0] <= WORKSPACE_X_RANGE[1])
        & (non_ground_points[:, 1] >= WORKSPACE_Y_RANGE[0])
        & (non_ground_points[:, 1] <= WORKSPACE_Y_RANGE[1])
        & (non_ground_points[:, 2] >= MIN_OBJECT_Z)
        & (non_ground_points[:, 2] <= 0.25)
    )

    workspace_points = (
        non_ground_points[
            workspace_mask
        ]
    )
    workspace_cloud = o3d.geometry.PointCloud()
    workspace_cloud.points = o3d.utility.Vector3dVector(
        workspace_points
    )

    labels = np.array(
        workspace_cloud.cluster_dbscan(
            eps=0.015,
            min_points=20,
            print_progress=False
        )
    )

    print("Cluster labels:", np.unique(labels))

    print(
        "Workspace points:",
        len(workspace_points)
    )
    for label in np.unique(labels):

        if label == -1:
            continue

        cluster_points = workspace_points[
            labels == label
        ]

        print(
            f"Cluster {label}: "
            f"points={len(cluster_points)}, "
            f"mean_z={cluster_points[:, 2].mean():.4f}"
        )

    candidate_clusters = []

    for label in np.unique(labels):

        if label == -1:
            continue

        cluster_points = workspace_points[
            labels == label
        ]

        num_points = len(cluster_points)
        mean_z = cluster_points[:, 2].mean()

        if (
            num_points >= CLUSTER_MIN_POINTS
            and mean_z >= CLUSTER_MIN_MEAN_Z
        ):
            candidate_clusters.append(
                (
                    label,
                    num_points
                )
            )
    if len(candidate_clusters) == 0:
        return None, None

    object_label = max(
        candidate_clusters,
        key=lambda item: item[1]
    )[0]

    object_points = workspace_points[
        labels == object_label
    ]

    print("Selected object cluster:", object_label)
    print("Object points:", len(object_points))

    object_cloud = o3d.geometry.PointCloud()
    object_cloud.points = o3d.utility.Vector3dVector(
        object_points
    )

    # o3d.visualization.draw_geometries([
    #     object_cloud
    # ])
    # -------------------------
    # 8. Estimate object yaw with 2D PCA
    # -------------------------

    object_xy = object_points[:, :2]

    object_center_xy_mean = np.mean(
        object_xy,
        axis=0
    )

    centered_xy = (
        object_xy
        - object_center_xy_mean
    )

    cov_xy = np.cov(
        centered_xy,
        rowvar=False
    )

    eigenvalues, eigenvectors = np.linalg.eigh(
        cov_xy
    )

    principal_axis = eigenvectors[:, -1]

    estimated_yaw = np.arctan2(
        principal_axis[1],
        principal_axis[0]
    )
    # -------------------------
    # 9. Estimate geometric center
    # -------------------------

    long_axis = principal_axis

    short_axis = np.array([
        -long_axis[1],
        long_axis[0]
    ])

    object_axes_2d = np.column_stack([
        long_axis,
        short_axis
    ])

    object_xy_aligned = (
        object_xy
        @ object_axes_2d
    )

    x_min = object_xy_aligned[:, 0].min()
    x_max = object_xy_aligned[:, 0].max()

    y_min = object_xy_aligned[:, 1].min()
    y_max = object_xy_aligned[:, 1].max()

    center_aligned = np.array([
        (x_min + x_max) / 2,
        (y_min + y_max) / 2
    ])

    center_world_xy = (
        center_aligned
        @ object_axes_2d.T
    )

    z_min = object_points[:, 2].min()
    z_max = object_points[:, 2].max()

    center_z = (
        z_min + z_max
    ) / 2

    object_center_est = np.array([
        center_world_xy[0],
        center_world_xy[1],
        center_z
    ])

    return (
        object_center_est,
        estimated_yaw
    )
