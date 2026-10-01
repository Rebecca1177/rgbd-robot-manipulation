# Day 2 工程重构验证（2026-10-01）

Day 2 Complete ✅（工程拆分与 DIRECT benchmark 验证；GUI 视觉检查待人工完成）

## 实际结果

| 指标 | 原版 | 重构版 |
| --- | --- | --- |
| trials | 5 | 5 |
| 抓取成功 | 5/5 | 5/5 |
| 平均位置误差 | 13.103116926994705 mm | 13.103116926994705 mm |
| 平均 yaw 误差 | 0.9428506138756731° | 0.9428506138756731° |
| 各 trial 数值字段最大差异 | — | 0.0 |

比较包括 success、failure_reason、position_error_mm、yaw_error_deg、object_height 和汇总结果。不是仅对四舍五入后的输出作比较。

## 验证条件与证据

- Windows，项目 `.venv_robot`：Python 3.10.7、NumPy 2.2.6、Open3D 0.20.0。
- NumPy 与 Open3D seed=42；OMP_NUM_THREADS=1；两边均为 PyBullet DIRECT。
- 新版直接执行 `scripts/run_benchmark.py --trials 5 --seed 42 --output ...`。
- 旧版通过外部 harness 执行原主程序，只将连接模式从 GUI 切换为 DIRECT；不修改历史文件。
- 保留原仿真时间步、sleep、渲染调用、随机采样顺序、noise/dropout、分割/PCA、IK、抓取和评估。
- 15 个函数完整 AST、全部配置赋值以及 benchmark 循环/统计 AST 一致。
- 拆分模块逐个通过 import 检查，无循环依赖。
- `results/baseline_seed42.json`、`results/refactored_seed42.json`：完整逐次数据。
- 对应 `.log`、`results/source_check.log` 和 `results/comparison.log`：运行与核对日志。
- 历史文件 SHA-256：`f024b5c70f37108131cc2f1bd6d0e98a01c2c9946ca0e84b5eee23f42a42c358`，验证前后不变，且与上传版本一致。

## 实现与问题处理

模块职责、完整文件清单及运行命令见 `DAY2_REFACTOR.md`。以 `src/pipeline.py` 保留完整实验顺序，将单次 metrics 与依赖 pipeline 的 benchmark 分开，避免循环依赖。公共常量集中在 config；函数实现未改写。

项目存在多套环境；`.venv310` 缺少 PyBullet，改用已安装全部依赖的 `.venv_robot`，未额外安装依赖。工程已有未提交内容，本次不修改这些内容。

## 验证边界与下一步

本结果证明上述固定输入与环境下的重构一致性，不是总体鲁棒性保证，也不宣称 GUI 与 DIRECT 渲染相同。GUI 单次入口尚需人工观察。原版空 cluster 返回空值后未处理，以及 IK 验证不检查姿态/碰撞等行为全部保留。后续先完成 GUI 检查，再整理 README 与实验说明；算法问题单独处理。
