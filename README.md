# 无极视频创作

`wuji-video-creation` 是影视技能的唯一源码。现有入口 `skills/seedance-film-production/` 升级为 **Skill 3.2.0 / Schema 2.0**，沿用 Codex、Grok Build、Hermes 的共用安装方式。

## 创作流程

**短剧剧本 → 文字分镜 → 必要资产 → 宫格分镜图（彩色／黑白线稿） → 视频提示词**

故事成立、分镜有效、资产准确、生成可控。前四阶段确认实际成果，宫格通过后直接交付提示词；不另设资产提示词、定脸补图或最终提示词审批。默认交付到图片和视频提示词，不自动生成视频或剪辑成片。

画幅由用户要求确定，新模板不默认横屏；竖屏项目按单格9:16设计。生成宫格前交付中文导演稿，串联原剧情、镜头、空间站位、逐格状态和实际提示词；结构测试通过不等于画面验收通过。

剧本采用中文场标与可演正文；分镜默认六列，镜数和时长由事件决定。优先复用素材，人物先半身定脸，按镜头补视图；内置 imagegen 生成和编辑。宫格可选彩色或黑白线稿，资产审阅时一并选择，已明确则不再询问；自适应格数、短行和分页，镜号映射放在图外。宫格控制构图与动作，资产控制身份、服装和最终外观；彩色宫格可补充光色。

确认绑定成果版本和直接依赖。改对白重验相关表演/时长/声音/提示词；改共享外观覆盖相关引用；只改提示词措辞不回退剧本。global revision 只记录变更。模型限制在实际编译入口核验，不把旧资料参数当作当前事实。

## 状态、兼容与验证

- [技能入口](skills/seedance-film-production/SKILL.md)
- [状态协议与 API](skills/seedance-film-production/references/state-schema.md)
- [项目状态](docs/project-state.md)
- [本次环境与验证记录](docs/integration-3.0-validation.md)

1.x 项目继续使用原校验逻辑。显式迁移命令创建新文件并保留全部旧数据、ID、媒体引用和批准记录；不自动给新结构盖批准章，旧画板不冒充黑白线稿，不要求历史项目全部重做。

```powershell
python -m unittest discover -s skills/seedance-film-production/scripts -p "test_*.py"
python skills/seedance-film-production/scripts/validate_project_state.py skills/seedance-film-production/assets/project-state.template.json
python scripts/validate-film-skill-structure.py
python skills/seedance-film-production/scripts/migrate_project_state.py OLD.json NEW.json
```

Python 需3.10+。若系统 python 仅是商店别名，可用 Codex 的已核实 Python 运行时路径执行。

## 安装同步

源码校验后使用 `scripts/sync-film-skill.ps1`。Codex 和 Hermes 是副本，Grok Build 是指向 Codex 副本的 Junction，均不单独编辑。

```powershell
pwsh -File scripts/sync-film-skill.ps1 -Target Codex
pwsh -File scripts/sync-film-skill.ps1 -Target Grok
pwsh -File scripts/sync-film-skill.ps1 -Target Hermes -HermesDestination "<实际 Hermes 技能目录>/creative/seedance-film-production"
pwsh -File scripts/sync-film-skill.ps1 -Target All -HermesDestination "<实际 Hermes 技能目录>/creative/seedance-film-production" -Check
```

Hermes 优先使用实际 HERMES_HOME 或已存在的用户目录；未知时要求显式路径，不假定旧电脑 WSL。同步覆盖前备份已改变的安装副本，遇到未知额外文件拒绝覆盖；检查模式不写入。Grok Bot 是独立应用，本脚本不修改其配置。

## 仓库和协作边界

动画导演、Visual Studio、ComfyUI 和备份仓库保持独立，不搬迁应用代码或删除历史仓库。用户参考文件只提炼方法，不整包重复加载。
品牌协作 SOP 保留：`品牌AI剪辑协作SOP_v2.pdf`（文档V1.1）是推荐团队协作基线，V1为历史对照；PDF不原地覆盖。外部 Google Sheet 的负责人、审核、云端验收和发布管理不进入影视状态。

开始工作读取 [AGENTS.md](AGENTS.md) 和项目状态；一个任务一个负责人，使用各智能体专用分支/隔离目录。推送前 fetch/rebase，检查暂存差异，通过 PR 更新 main，不强推。提交正文标明 Agent，Codex 负责最终质检。
默认不提交认证资料、用户原始资料、Agent 会话、缓存和大型媒体。生成图保存在本地 output/，版本库只保存脱敏方法和验证证据。
