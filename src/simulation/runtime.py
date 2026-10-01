"""Explicit connection lifetime and optional reproducibility controls."""

import numpy as np
import open3d as o3d
import pybullet as p


def connect_simulation(gui=False, seed=None):
    if seed is not None:
        np.random.seed(seed)
        o3d.utility.random.seed(seed)
    client = p.connect(p.GUI if gui else p.DIRECT)
    if client < 0:
        raise RuntimeError("Could not connect to PyBullet")
    return client


def disconnect_simulation(client):
    if p.isConnected(client):
        p.disconnect(client)
