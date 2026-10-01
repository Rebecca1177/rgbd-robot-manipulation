# Day 2 收尾（2026-10-01）

Day 2 Complete ✅（模块化工程、文档与已有验证证据整理；展示视频待录制）

## 本次交付

- `README.md`：英文 GitHub 项目主页，包含 Overview、System Pipeline、Project Structure、Methodology、Robustness Evaluation、Results、Limitations、Future Work、How to Run。
- `requirements.txt`：当前模块化 pipeline 的依赖清单；NumPy/Open3D 按已验证版本固定，标准 PyBullet 包用于新环境。现有环境元数据为 `pybullet_arm64==3.2.8`，不将清单宣称为精确环境锁。
- `notes/demo_guide.md`：录制步骤、当前相机参数及三视图取舍。
- `notes/day2_closeout.md`：本次检查记录和后续行动。

未修改任何 Python 文件、配置值、历史实验记录或原始 JSON；未增加算法、模型、可视化钩子或 PyBullet 流程。历史 roadmap 保留在原目录，README 不再把长期目标当作现有功能。

## 核对结果

- 已实际执行两个入口的 `--help`：均正常，CLI 参数与 README 一致。
- 已实际执行 `tests/check_refactor.py`：15 个函数体/签名、全部配置赋值、benchmark 循环/统计一致；5 次保存结果及汇总一致，最大数值差异 0.0。
- 环境核对：Python 3.10.7，NumPy 2.2.6，Open3D 0.20.0，PyBullet 模块可导入，build 2026-03-13；distribution metadata 为 `pybullet_arm64 3.2.8`。
- 本次没有重跑完整仿真实验或创建新环境。GUI 验收来自用户在引用对话中的确认：视角可用、pre-grasp/垂直接近/闭爪/lift 跟随正常。
- ground truth 数据流已查阅源码：场景生成后只进入评估（含 IK 失败分支的误差统计），不参与感知和抓取目标生成。
- 历史 5 mm + 2% dropout 的 4/5 与 seed 42 重构对照的 5/5 分开展示；未伪造 ideal baseline 数值、缺失样本量或历史 seed。

## 展示取舍

没有现成独立 visualization 模块；只有 GUI camera 初始化，Open3D draw 调用处于注释状态。同步三视图需要在运动过程中接入采集与合成，不符合此次低改动收尾目标，列为 future polish。当前建议单视角视频。

## 当前完成度与下一步

当前几何感知 → 抓取规划 → IK → 接近/抓取/抬升 → 评估已经完成模块化及重构验证；本次文档收尾完成。它是 simulation-only、单次感知驱动的执行系统；不宣称放置、实时视觉伺服、多物体泛化或真实机器人验证已完成。

用户下一步：直接按 demo guide 录制 30–60 秒视频，再审阅英文 README 的项目定位。后续可进入简历表达与项目讲解准备；无需继续修改核心算法，也无需重复搬运上下文。

保留的边界：空 cluster 未处理；IK 未做姿态/碰撞验收；中心 min/max 对异常点敏感；结果 JSON 未保存完整配置快照。后续功能修改另行验证。
