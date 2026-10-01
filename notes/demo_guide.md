# Demonstration Guide

Record a 30–60 second single-view clip showing the scene, pre-grasp, vertical approach, gripper closure, and object-following lift. Include the terminal result if useful, with units and the selected seed. Caption the system as “Geometry-based RGB-D perception-guided grasping in simulation.” Do not label it real-time visual servoing or learning-based manipulation.

Run from the project root:

```powershell
.\.venv_robot\Scripts\python.exe scripts/run_single_trial.py --seed 42
```

Current GUI camera defaults: distance 1.5 m, yaw 45°, pitch −25°, target [0.45, 0.0, 0.25] m. These display settings are separate from the two perception cameras. The project owner has already confirmed visibility and the full grasp/lift sequence. Press Enter in the terminal to close the demonstration after evaluation.

The current final pipeline does not show a live point-cloud window: its Open3D draw call is commented out. Do not imply that built-in PyBullet panels are custom three-view output or that the demo displays segmentation overlays.

## Three-view decision

No independent visualization module is present. Scene setup only initializes the PyBullet GUI camera. Synchronized main/top/side recording would require render/capture hooks during motion and video composition; a standalone module alone would not capture intermediate motion. Defer this to future polish to preserve the verified execution flow. Single-view recording is sufficient for the current release.

For a later visualization task, keep camera rendering independent of perception and random sampling, make recording opt-in, and recheck behavioral equivalence. No such changes were made in this closeout.
