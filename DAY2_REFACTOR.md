# Day 2 工程重构

本次以 `exercises/final_version.py` 为唯一算法基准。原文件继续保留并可运行；已有 exercises、notes、data、geometry/rotation.py 均不覆盖。

## 模块职责

| 文件 | 职责 |
| --- | --- |
| `src/config.py` | 原脚本全部配置常量，保留原数值 |
| `src/simulation/scene.py` | 场景、Panda、随机物体位置/尺寸/yaw |
| `src/simulation/runtime.py` | PyBullet 连接/释放，可选随机种子 |
| `src/perception/rgbd.py` | RGB-D 采集、深度噪声、dropout |
| `src/perception/pointcloud.py` | 深度转点云、相机到世界坐标变换 |
| `src/perception/segmentation.py` | 双相机融合、RANSAC、工作空间/MIN_OBJECT_Z 过滤、DBSCAN、cluster 筛选、PCA 与几何中心 |
| `src/planning/grasp.py` | 抓取姿态、hand offset、pre-grasp |
| `src/control/robot.py` | 查找 hand link 和 finger joints |
| `src/control/ik.py` | 关节限位/FK 验证、多 seed IK |
| `src/control/motion.py` | 关节轨迹、Cartesian waypoints |
| `src/control/gripper.py` | 手指打开/闭合 |
| `src/evaluation/metrics.py` | 抓取成功与位置/yaw 误差 |
| `src/evaluation/benchmark.py` | 原 benchmark 循环与统计 |
| `src/pipeline.py` | 原 `run_trial`，串联完整抓取流程 |
| `scripts/run_single_trial.py` | GUI 单次演示，结束后按 Enter 关闭 |
| `scripts/run_benchmark.py` | 批量运行，默认 5 次，可保存 JSON |
| `tests/check_refactor.py` | 原函数/配置/统计结构核对，逐次 benchmark 结果对照 |
| `tests/run_regression.py` | 可重复运行旧版与新版的 5 次真实仿真对照 |

`src` 及六个子目录补充 `__init__.py`。现有 `src/geometry/rotation.py` 无需迁移或改写；相机变换按本次要求放在 perception。依赖方向为入口 → benchmark/pipeline → 各职责模块 → config；metrics 不导入 pipeline，避免循环依赖。模块导入不会启动仿真。

## 运行

在项目根目录使用已验证的 `.venv_robot` 环境（Python 3.10.7、NumPy 2.2.6、Open3D 0.20.0，PyBullet 构建日期 2026-03-13）。现有 `.venv310` 缺少 PyBullet，不用于本次验证。

```powershell
# GUI 单次演示
.\.venv_robot\Scripts\python.exe scripts/run_single_trial.py --seed 42

# 默认 DIRECT 批量运行；保留原时间步及 time.sleep
.\.venv_robot\Scripts\python.exe scripts/run_benchmark.py --trials 5 --seed 42 --output results/benchmark.json

# 与旧入口一样使用 GUI
.\.venv_robot\Scripts\python.exe scripts/run_benchmark.py --gui --trials 5

# 运行历史版本（原行为：GUI，5 次）
.\.venv_robot\Scripts\python.exe exercises/final_version.py

# 核对源代码迁移与已保存的对照结果
.\.venv_robot\Scripts\python.exe tests/check_refactor.py --original exercises/final_version.py --old-results results/baseline_seed42.json --new-results results/refactored_seed42.json

# 重新执行完整对照，默认保存至 results/regression
.\.venv_robot\Scripts\python.exe tests/run_regression.py
```

入口支持从其他工作目录用绝对路径启动。`--seed` 同时设置 NumPy 与 Open3D；不传入时保留随机行为。`--output` 为可选输出路径。GUI 演示可用 `--no-wait` 在评估后自动关闭。

## 一致性验证范围

15 个原函数的签名、默认参数、函数体保留，全部配置值保留。新代码只增加导入、连接生命周期、命令行参数和结果保存；原 benchmark 循环和均值计算保留。

对照运行使用相同环境、NumPy/Open3D seed=42、`OMP_NUM_THREADS=1`、PyBullet DIRECT。单线程仅用于验证时减少 Open3D 并行 RANSAC 的非确定性，程序默认不强制设置线程数。旧版测试通过外部验证脚本将主入口的 GUI 连接替换成 DIRECT；原文件未改动。相同种子不等于跨环境或 GUI/DIRECT 渲染结果必然完全一致。详细数据和日志见 `results/`。

## 后续人工检查

- 在桌面打开 GUI 演示，确认相机视角、接近、夹爪闭合和抬升观感。
- 空 cluster 时 `perceive_object` 返回 `(None, None)`，旧 pipeline 尚未处理，可能报错；本次未改变该行为。
- 原 IK 验证只核对关节限位与末端位置，未新增姿态误差或碰撞检查。
- 5 次固定种子对照用于验证重构一致性，不代表总体成功率；不同随机种子与 GUI 渲染需另行评估。
- 下一步可整理项目 README 和已有实验结果；任何算法修复另开明确任务。
