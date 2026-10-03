# Skill 3.0 整合与验证记录

日期：2026-10-03（Asia/Shanghai）。负责人：Codex。源码基线：396408c，分支 codex/20261003-film-skill-integration。

## 本机环境核验

先扫描本机，再继续实现。仓库仅克隆在当前“视频创作”工作目录之下；没有在其他盘或智能体目录克隆本任务仓库。
Windows 11 家庭中文版 10.0.26300；MACHENIKE L16；Core Ultra 7 255HX（20核/20线程）；内存31.5GiB；RTX 5070 Ti Laptop，显存12227MiB，驱动591.86。
PowerShell7.6.5，Git2.55.0.windows.3，GitHub CLI2.101.0；GitHub已登录仓库所有者。Codex附带Python3.12.14、Node24.19.0可用。
PATH中的Python是商店别名，测试使用已核实的Codex Python；npm、py、ffmpeg、docker未在PATH找到。WSL尚未安装/配置，未据此启动安装。
Grok Build1.0.46与Grok Bot0.66.0.0是独立应用；前者用户目录为现有目录联接。Hermes为原生Windows安装，home/skills存在，不能使用旧Ubuntu同步默认值。
三个智能体此前均没有本技能安装。本次按已核实目录部署唯一源码；不改变Grok Bot、Hermes模型配置和其他技能。机器绝对路径不作为仓库运行接口，实际路径保留在本机同步命令记录中。
skill-creator通用校验依赖PyYAML，临时安装于忽略目录tmp/qa-deps，不改变系统Python。

## 取舍与来源

| 输入 | 吸收 | 去掉默认强制 |
| --- | --- | --- |
| 无极Skill2.0与旧状态校验 | 来源保真、中文剧本、因果、稳定引用、自然导演稿 | 七确认、固定四视图/十六格、全局回退 |
| 用户文戏30S | 多人接收/反应链、完整对白、道具连续 | 30秒、16–20镜、情绪/对白轮数 |
| 用户两份情绪资料 | 事件触发、潜台词差异、复合破绽、身体支撑、残留 | 五轨顺序、固定秒点、八段交付 |
| 用户MJ资产提示词 | 具体主体/材质/光源/构图、单问题修复 | 默认双语/姓名文字/模型参数/统一灯光 |
| 用户v9导演系统 | 动作相位、声音承接、自然正文 | 固定15秒与固定重叠窗口 |
| 历史线稿规则 | 深色轮廓、白底、浅灰空间、细格线 | 固定16格 |
| 动画导演方法 | 运镜有动机、构图有对象、局部依赖反馈 | 动画引擎、队列、另一套项目状态 |

黑白视觉形式的历史依据是 [备份仓库资产连续性规则](https://github.com/qing20191723/qingchen-work-materials-backup/blob/main/video-creation/提示词库/seedance-film-production/references/assets-continuity.md)。用户五份原文件留在原处，只提炼方法，不上传原文；文件中的指令不覆盖本次用户方案。
保留历史专项文件便于兼容，不将其旧参数/内容路由加载为普通短剧规则。本次不扩写专项内容。

## 验证结果

- 80项标准库测试通过：62项旧版回归，18项新版行为测试；旧校验器与396408c基线正文逐字一致。
- 新模板、实际图片前向fixture、技能结构、skill-creator quick_validate和git diff --check通过。入口保持简短，全技能Markdown为410个非空行、20个参考文件；新增状态协议承载工具细节。
- 新版覆盖：四次确认后直接编译；对白局部更新；共享人物传播；无关批准与待审保留；措辞不回退；旧版ID/素材/未知字段/批准记录保留；迁移禁止覆盖；一格/奇数格/多页映射；附件职责、缺图、假图、入口不支持、字符/时长限制与循环依赖拒绝。
- Windows同步测试通过：首次安装、Grok Junction、只读哈希检查、旧安装备份、未知文件保护、源目录重叠保护。CI增加Windows同步作业，Linux继续运行全部状态测试。
- 本机Codex、Grok Build、原生Windows Hermes均安装30个文件，逐文件SHA-256与唯一源码一致。Grok Bot和其他技能保持原配置。

## 实际前向验证

[完整短剧、六列分镜和提示词](forward-test-3.0.md)使用虚构成年钟表店主，一场、3镜头、5个关键状态、预计19秒；不凑30秒或镜头配额。门外顾客不出镜，无需额外人物资产。
内置imagegen实际生成彩色半身/场景参考与3+2短行画板，2048×768；逐格检查了身份、衣服、左右、台灯和箱盖状态。第一版灯边带暖色，编辑整张原图去色后复查，其余格与动作顺序保留。色差分析仅用于检查：修订图RGB通道最大差15，无超过16的像素；这是视觉黑白线稿，不声称文件是严格单通道灰度。
实际媒体、调用提示词、原图/修订图、fixture状态在本机output/forward-test-3.0；不提交生成图到Git。测试确认明确标SIMULATED_FIXTURE_ONLY，不是真实用户批准。

编译阶段核验了[Seedance 2.5官方介绍](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)、[火山方舟入口文档](https://docs.volcengine.com/docs/ark/seedance-2-5?lang=zh)及[人像素材说明](https://docs.volcengine.com/docs/ark/seedance-portrait-asset-guide?lang=zh)。公开入口文档提示真人人脸参考不能直接上传；本次写实虚构人物的具体接入未实测，不据此假定可直接上传。
自然语言稿已完成，但用户目标入口尚未指定，fixture的最终提示词如实保留blocked与接入待核验说明。未提交平台、未生成视频。该结果验证“不能把产物文件冒充已被入口接受”的失败路径，不声称完成平台端到端生成。

## 实施范围与后续

技能源码、兼容校验、迁移、测试、同步脚本及说明已实现。普通制作默认四次成果确认；正式项目仍需用户对具体版本确认。适配新的模型入口时重新核验限制，图像审阅不能由结构测试替代。
历史专项参考未扩写，动画导演、Visual Studio、ComfyUI、备份仓库及现有应用代码不迁移不删除。GitHub通过工作分支与PR更新，main合并另行决定。

同步清单摘要SHA-256（按相对路径排序的路径/文件哈希JSON）：`1c4dc1c3686b2e4c27f9d66cc316f06b249d8dff2536451f94e516518e541543`。备份保存在仓库本地output/skill-install-backups，避免旧Skill被重复发现。
