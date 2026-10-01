# Day 1 鲁棒性收尾

Day 1 Complete ✅（工程鲁棒性阶段，不是早期 NumPy 几何 Day 1）

文档固化：2026-09-30。依据：用户提供的“每日机器人学习计划”历史测试结果与本次 `exercises/final_version.py` 静态核对。实验日期未另行推断；未重新运行 benchmark，未把缺失数据补写为零或成功。

## 冻结版本与验收

- 入口：`exercises/final_version.py`；代码不修改、不拆分、不另存行为不同的实现。
- SHA-256：`f024b5c70f37108131cc2f1bd6d0e98a01c2c9946ca0e84b5eee23f42a42c358`。
- Python AST 语法检查通过，不导入仿真依赖、不启动 GUI；这不等于本次运行验证。
- 原有工作区包含未提交修改和未跟踪文件，本次不回退、不清理这些内容。
- README 保留旧学习路线并明确历史范围；旧 Day01 几何笔记和 day_11_closeout 等保留为历史学习记录，不将过去的未完成功能误当作当前工程状态。

## 实现检查清单

| 要求 | 当前实现与参数 |
|---|---|
| 随机 workspace | `setup_scene` 在 X=[0.20,0.70]、Y=[-0.40,0.40] m 内采样位置，并依据 yaw 后投影半尺寸留边界；不是每次随机改变 workspace 范围 |
| 随机尺寸 / yaw | 长 [0.08,0.12]、宽 [0.04,0.07]、高 [0.03,0.05] m；yaw [-π,π] |
| Gaussian noise | `capture_rgbd` 在转换后的米制深度上加零均值 Gaussian，当前 σ=0.005 m |
| 2% dropout | 独立像素 mask，置为 CAMERA_FAR=3 m；感知保留 depth <2.99 m |
| 双相机融合 | 两个 640×480 RGB-D，相机 [0.7,±0.7,1.2] m，观察 [0.45,0,0]；world 变换后融合 |
| RANSAC | `segment_plane(distance_threshold=0.003, ransac_n=3, num_iterations=1000)`，剔除平面 inliers |
| 高度 / workspace | XY crop，MIN_OBJECT_Z=0.008 m ≤ z ≤0.25 m |
| DBSCAN | eps=0.015 m，min_points=20，忽略 label=-1 |
| 候选筛选 | 点数 ≥100 且 mean_z ≥0.015 m；选合格候选中点数最多的 cluster |
| PCA / 几何中心顺序 | 提取 object_points 后做 XY PCA；在主轴对齐坐标求 XY min/max 中点，旋回 world；Z 为 min/max 中点 |
| 感知 → 操作 | `build_grasp_pose` 使用视觉估计，hand offset=0.105 m，pre-grasp=0.10 m，lift=0.15 m |
| 评估隔离 | true position / yaw 用于场景生成与 evaluation（含 ik_failed 误差统计），不传入 perceive_object / build_grasp_pose / IK 目标；真实物体尺寸不作为感知输入 |

## 测试条件与历史结果

| 条件 / 阶段 | 样本量 | success | mean position error (mm) | mean yaw error (deg) |
|---|---:|---:|---:|---:|
| 扩大 workspace：X=[0.2,0.7], Y=[-0.4,0.4] m | 未记录 | 100% | 3.71 | 0.66 |
| 随机物体尺寸，温和范围 | 3 | 100% | 3.82 | 1.73 |
| 2 mm Gaussian noise，修复前，异常记录 A | 未记录 | 未记录 | 26.48 | 22.13 |
| 2 mm Gaussian noise，修复前，异常记录 B | 未记录 | 未记录 | 302.49 | 60.54 |
| 高度过滤 + DBSCAN 后，2 mm noise | 未记录 | 100% | 7.63 | 0.37 |
| 5 mm noise | 10 | 10/10，100% | 12.37 | 1.39 |
| 增强 cluster selection 后，5 mm noise | 3 | 100% | 12.58 | 0.15 |
| 8 mm noise | 第 1 次观察 | 首次即抓偏；无汇总成功率 | 未记录 | 未记录 |
| 5 mm Gaussian noise + 2% depth dropout | 5 | 4/5，80% | 13.57 | 1.17 |

noise 数值表示标准差 σ，不是最大误差。仅最后一组明确组合 2% dropout；其它 noise-only 历史结果不能用当前 dropout 默认配置直接重现。历史温和随机尺寸测试的精确参数、未列出的试验数和随机 seed 未完整保留；上表与当前代码参数分开记录，不能倒推所有历史批次均采用最终配置。理想 baseline 据历史描述稳定，没有额外编造其试验数或误差。

### 最后一组逐次记录：5 mm + 2% dropout

| Trial | success | position error (mm) | yaw error (deg) | object points | selected label |
|---|---|---:|---:|---:|---:|
| 1 | True | 11.59 | 1.27 | 1091 | 1 |
| 2 | True | 16.63 | 0.19 | 1138 | 2 |
| 3 | True | 13.55 | 1.07 | 1364 | 0 |
| 4 | True | 12.57 | 0.64 | 1328 | 0 |
| 5 | False | 13.54 | 2.70 | 1201 | 0 |

成功 4/5=80%。已显示两位小数的逐次数据均值为 13.576 mm / 1.174°；程序原始精度汇总为 **13.57 mm / 1.17°**。保留原始汇总，不因逐次打印舍入而改写成 13.58 mm。cluster label 每次可变化，不是固定物体身份。

## 指标定义

- Position error：视觉中心与场景生成时真实中心的三维欧氏距离 ×1000，单位 mm；不是末端跟踪误差，也不是运动后物体位移。
- Yaw error：`abs(degrees((estimated_yaw - true_yaw + pi/2) % pi - pi/2))`，消除 PCA 180° 轴歧义。
- Success：执行 lift 后读取物体中心高度，world z ≥0.08 m 为 True；未测试长期保持或 place。
- 主程序 NUM_TRIALS=5；对返回结果的成功率、位置/yaw 误差取平均，含返回的失败试验。感知异常可能直接终止，未形成完整失败计数。

## Failure analysis

2 mm noise 暴露了 ground residual 污染。RANSAC 距离阈值外的地面点仍可进入 workspace；若当成目标点，PCA 方向会偏移，少量远处 outlier 会显著拉大 min/max，造成 26.48 mm /22.13° 以及 302.49 mm /60.54° 等历史异常。几何中心估计的前提是输入已是目标 cluster，不能把所有非平面点直接视为物体。

修复依次为：8 mm 高度门限压制贴地残留 → DBSCAN 分离密集物体与噪声 → 按点数和 mean_z 过滤候选 → 对选中 cluster 做 PCA 和边界中心估计。2 mm 下恢复 100% 的已报告结果；5 mm 的十次测试全成功。增强候选筛选后的三次仍成功，但样本量与场景不同，不能据此声称 yaw 精度有统计显著提升。

8 mm 首次抓偏，仅能作为 failure-boundary 观察，不是已测定的精确失效阈值。5 mm + dropout 的 4/5 说明该批次存在退化；第 5 次失败仍有 13.54 mm /2.70° 的有限感知误差，感知偏差和抓取容差共同作用是合理假设，但不能仅凭汇总排除 IK、碰撞、接触或执行因素，也不能独立证明 dropout 导致失败。

## Baseline / robustness story

Ideal baseline -> stress test -> noisy ground residual failure -> height filter + DBSCAN -> robustness restored -> stronger noise/dropout shows degradation boundary

核心收获：以 stress test 揭示感知输入污染，先修复分割，再评价位姿与抓取；成功率和位姿误差要同时看，保留失败样本，不把少量 100% 结果当作普遍可靠性保证。

## 已知限制与保留事项

当前仍是单次视觉估计后的 approach / grasp / lift，没有 place、重观测闭环或完整避碰。固定世界高度门限依赖平地与当前物体高度；最大候选策略依赖单物体场景。RANSAC 未显式验证地面法向/高度。min/max 仍易受残余 outlier、噪声、遮挡与高度截断影响；近方形物体 PCA 方向可能不稳定。

无合格 cluster 返回 `(None,None)`，`run_trial` 随后直接调用 `build_grasp_pose`，可能在 `.copy()` 处出错。此处记录为已知边界，不在收尾时改写用户学习代码。pre-grasp IK 只检查限位和 FK 位置，未检查姿态/碰撞；沿途 waypoint IK 未复用该检查。`perceive_object` docstring 仍写 workspace_points，实际返回中心/yaw，属于保留的旧注释。

没有固定 seed、配置快照、自动逐次结果落盘或完整历史日志；历史测试使用的精确中间代码版本不可由最终文件反推。本次冻结最终源码 hash，不声称恢复了每一批历史实现。

## Day 2 计划（未执行）

仅记录计划，尚未执行：正式拆分 `src/`；建立 `run_single_trial.py` / `run_benchmark.py`；统一配置和最终 benchmark；三视图 demo；README / pipeline polishing；简历项目描述和面试讲法。仓库已有 `src/` 目录不代表此次已完成拆分。
