# 无极视频创作

空间资产入口：[《秘密教学》主角家空间资产建模](assets/《秘密教学》主角家空间资产建模/README.md)。当前唯一保留用户指定的 V4 直走廊布局；错误 V5 与其他旧建模版本已清理。先核对当前平面图，正式场景出图暂停。模型与必要参考以 Git LFS 保存在专用私有分支。

`wuji-video-creation` 是无极 AI 视频创作与品牌剪辑协作项目的私有事实源，用于维护协作 SOP、版本规则、AI 影视生产方法及后续可复用的项目文档。

## 当前基线

| 文件 | 文档版本 | 定位 |
| --- | --- | --- |
| `品牌AI剪辑协作SOP_v1.pdf` | V1.0 | 历史基线：四阶段流程、脚本/资产/画面三道锁、A/B 类修改分级。 |
| `品牌AI剪辑协作SOP_v2.pdf` | V1.1 | 当前推荐基线：增加云端初版验收、无水印母版与有水印发布版双版本交付。 |

影视生产方法的可执行事实源是 `skills/seedance-film-production/`。Skill 包版本为 `2.0.0`，项目状态模板为 Schema `1.9`，兼容读取 `1.1`–`1.8` 并提示升级。完整项目保留 G1–G7 确认门禁，对用户交付剧本包、导演分镜包、资产包和模型编译包；专科入口仍可单独进行剧本、对白、表演、平台节奏和后期声音诊断。

创作以“故事覆盖—资产锁定—可直拼单元”为主轴：剧本先按中文短剧场标和可演正文讲清人物行动，不预写摄影术语；分镜先确定承载主要剧情的观看位置，只增加能带来揭示、反应、悬念、强调或空间重建的补充视点。下一单元继承人物、环境、身体、服装、道具、声线、情绪与因果，但允许摄影机从新的专业位置进入。正常段在批准分镜后按视觉信息量决定十六宫格是否必要，并逐段独立编译 Seedance 2.5；成人段不制作十六宫格，使用必要资产逐段编译 Wan 3.0。各单元依赖批准 Canon 和资产，不依赖上一条已生成视频，因此可以并行生成并按 `assembly_contract` 顺序直接切接。Wan 3.0 提示词官方上限为 20,000 字符；Seedance 2.5 官方未公布字符上限，两路均禁止静默截断。

G1–G7 只用于锁定影视创作内容，不是团队视频协作确认表。外部 Google Sheet 继续管理负责人、审核意见、云端验收、交付版本和发布状态；其表结构与工作流不写入影视 Skill，只有表中已经批准的创作事实可作为 Skill 输入。

PDF 原件只做版本留档，不原地覆盖。修改内容时新增明确版本号的源文件或 PDF，并在 `docs/project-state.md` 更新当前基线。

## 仓库边界

可以提交：

- SOP、需求模板、验收表、交付清单和版本说明；
- 已脱敏的剧本、分镜、提示词、资产清单和连续性台账；
- 可复用的小型脚本、配置示例和校验工具；
- 经验证的 Codex/Grok 共用影视 Skill、参考规则与项目状态模板；
- 经确认需要长期维护的小型参考图与文档。

默认不提交：

- `tmp/` 中的 PDF 渲染页、缓存和中间文件；
- 成片、渲染输出、大型音视频及可重新生成的派生资产；
- 客户未授权素材、账号信息、Token、Cookie、API Key、私钥和本机认证文件；
- Grok、Codex 或其他工具的原始会话和调试日志。

## Codex、Grok Build 与 Hermes 协作入口

三个智能体开始工作前都必须读取：

1. `AGENTS.md` - 提交、分支、冲突与 README 维护规则；
2. `docs/project-state.md` - 当前基线、活动任务和下一步；
3. 与当前任务直接相关的文档。

影视任务还必须读取 `skills/seedance-film-production/SKILL.md`。该目录是唯一源码；Codex 与 Hermes 使用同步副本，Grok 使用指向 Codex 安装副本的 Junction。三处安装目录都不得独立编辑。

默认规则：一个任务、一个负责人、一个隔离工作目录。Codex 使用 `codex/<日期>-<主题>`，Grok Build 使用 `grok/<日期>-<主题>` 与独立 worktree，Hermes 使用 `hermes/<日期>-<主题>` 与独立 clone。三者都可创建 PR 和提交测试证据；最终质检汇总与 `main` 合并仅由 Codex 完成。

同步或检查本机 Codex Skill：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-film-skill.ps1 -Target All
powershell -ExecutionPolicy Bypass -File scripts/sync-film-skill.ps1 -Target All -Check
```

## 提交流程

```powershell
git fetch origin
git status
git switch -c codex/20260824-example
# 或：git switch -c grok/20260824-example
# 或：git switch -c hermes/20260824-example

# 修改并验证后
git add <明确文件>
git diff --cached
git commit -m "docs: describe the change"
git pull --rebase origin main
git push -u origin HEAD
```

- `main` 只接收已经检查过的完整变更，不强推，不直接覆盖远端历史。
- 提交类型优先使用 `docs:`、`feat:`、`fix:`、`chore:`。
- 提交正文末尾写 `Agent: Codex`、`Agent: Grok Build` 或 `Agent: Hermes`；人工提交写 `Agent: Human`。
- Grok Build 与 Hermes 可以创建 PR 和提交审查证据，但不得发布最终质检汇总或合并 `main`。
- 提交前必须检查暂存区，不使用无范围的批量提交来混入缓存、认证文件或大型媒体。
- 发现远端已有同文件改动时，停止写入，先同步并解决差异；不得用 `--force` 掩盖冲突。

## README 维护规则

README 只保存稳定、对接手者有用的信息：项目定位、当前基线、仓库边界、目录入口和协作规则。

以下变化必须更新 README：

- 项目定位、交付物或事实源发生变化；
- 当前推荐 SOP 或核心工作流升级；
- 新增、删除或重命名关键目录与入口文件；
- Codex/Grok 的协作、提交或安全规则改变。

以下内容不要写进 README：临时任务进度、聊天摘要、单次排障过程、账号凭据和详细变更流水。动态状态写入 `docs/project-state.md`，版本变化写入提交历史或后续 `CHANGELOG.md`。

## 当前目录

```text
.
├── AGENTS.md
├── README.md
├── 品牌AI剪辑协作SOP_v1.pdf
├── 品牌AI剪辑协作SOP_v2.pdf
├── docs/
│   └── project-state.md
├── scripts/
│   └── sync-film-skill.ps1
└── skills/
    └── seedance-film-production/
        ├── SKILL.md
        ├── assets/
        ├── references/
        └── scripts/
```
