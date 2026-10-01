import numpy as np


def rotation_matrix_z(theta):
    """Return the active rotation matrix for a rotation about the z-axis."""
    return np.array(
        [
            [np.cos(theta), -np.sin(theta), 0.0],
            [np.sin(theta), np.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix_x(theta):
    """Return the active rotation matrix for a rotation about the x-axis."""
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, np.cos(theta), -np.sin(theta)],
            [0.0, np.sin(theta), np.cos(theta)],
        ]
    )


def rotation_matrix_y(theta):
    """Return the active rotation matrix for a rotation about the y-axis."""
    return np.array(
        [
            [np.cos(theta), 0.0, np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-np.sin(theta), 0.0, np.cos(theta)],
        ]
    )

def homogeneous_transform(R, t):
    """Build a 4 x 4 homogeneous transform from rotation and translation."""
    R = np.asarray(R, dtype=float)
    t = np.asarray(t, dtype=float)

    if R.shape != (3, 3):
        raise ValueError(f"R must have shape (3, 3), got {R.shape}")
    if t.shape != (3,):
        raise ValueError(f"t must have shape (3,), got {t.shape}")

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T
