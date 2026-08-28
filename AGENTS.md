# 无极视频创作 Agent 协作规则

本文件同时约束 Codex、Grok Build、Hermes 和其他会修改本仓库的智能体。规则适用于仓库根目录及全部子目录。

## 1. 开始任务

1. 先运行 `git status --short --branch`、`git fetch origin`，确认当前分支和未提交修改。
2. 阅读 `README.md` 与 `docs/project-state.md`。
3. 影视生产、剧本会诊、对白精修、平台节奏或后期声音任务必须读取 `skills/seedance-film-production/SKILL.md`，并只加载该 Skill 路由到的参考文件。
4. 明确本轮负责人、目标文件、验证方式和是否涉及外部上传。
5. 如果另一智能体正在修改相同文件，保持只读并等待交接；不要并行覆盖。

## 2. 分支与 worktree

- Codex 分支：`codex/YYYYMMDD-topic`。
- Grok Build 分支：`grok/YYYYMMDD-topic`。
- Hermes 分支：`hermes/YYYYMMDD-topic`。
- 人工分支：`human/YYYYMMDD-topic`。
- 一个任务只由一个智能体负责写入；其他智能体可以审查，但不得同时实现。
- Codex、Grok 与 Hermes 不得共用同一工作目录进行并行写入。Grok 默认使用独立 worktree，Hermes 默认使用独立 clone。
- `main` 不强推、不改写历史、不提交未经检查的临时产物。

## 3. PR 与最终质检权限

- Codex、Grok Build、Hermes 都可以提交分支、推送并创建 PR，也可以在 PR 中提供审查发现和测试证据。
- Grok Build 与 Hermes 不得填写“Codex 最终质检”区、发布最终质检结论或执行 `main` 合并。
- 只有 Codex 汇总提交谱系、差异范围、Schema/Canon 影响、测试、三端同步哈希和未解决风险，并决定是否合并。
- 所有智能体默认通过 PR 进入 `main`，不得直接推送 `main`。仓库平台无法提供硬性分支保护时，本规则、PR 模板和 CI 仍然有效。

## 4. 同步与冲突

- 开始编辑前获取远端状态；推送前执行 `git pull --rebase origin main` 或在对应分支上显式 rebase。
- 只暂存本任务文件，并用 `git diff --cached` 检查最终提交。
- 遇到同文件远端修改时停止自动提交，先比较双方意图；不能确定时交给用户决定。
- 不使用 `git reset --hard`、`git clean -fd`、`git push --force` 或其他可能丢失内容的命令。
- 不覆盖用户未提交修改，不把另一个智能体的变更据为本轮提交。

## 5. 提交规范

- 标题采用 `docs:`、`feat:`、`fix:`、`chore:` 等清晰前缀。
- 一个提交只表达一个可回滚意图。
- 提交正文记录验证结果，并以 `Agent: Codex`、`Agent: Grok Build`、`Agent: Hermes` 或 `Agent: Human` 标明负责人。
- 未通过对应校验的内容不得标为完成；PDF、图片和视频变更必须实际检查产物。

## 6. 文档事实源

- `README.md`：稳定定位、当前基线、目录入口和协作规则。
- `docs/project-state.md`：动态状态、活动任务、已确认决策和下一步。
- Git 历史：具体变化与责任人。
- README 不充当工作日志；临时过程和聊天记录不得写入 README。
- 更改当前 SOP 基线、仓库边界、关键入口或协作规则时，README 与项目状态必须同步更新。

## 7. 影视与资产规则

- `品牌AI剪辑协作SOP_v2.pdf` 是当前推荐基线，V1 仅作历史对照。
- `skills/seedance-film-production/` 是 Codex、Grok 与 Hermes 共用的影视生产 Skill 唯一源码；本机安装目录只是同步副本，不在安装处独立编辑。
- 修改 Skill 后先运行其标准库测试、项目状态校验和技能结构校验，再用 `scripts/sync-film-skill.ps1` 同步本机。
- 外部视频协作确认表或 Google Sheet 继续作为团队协作工具；不得把负责人、审核、意见汇总、云端验收、水印交付和发布状态复制进影视 Skill 或其项目状态模板。
- 已发布 PDF 不原地覆盖；新版本使用新文件名并说明替代关系。
- 剧本、资产、画面与交付状态使用稳定名称和版本号，避免静默改写已确认事实。
- `tmp/`、渲染输出和大型音视频默认不进 Git；确需版本管理时先评估 Git LFS 或外部资产存储。

## 8. 安全边界

- 禁止提交 Token、Cookie、API Key、私钥、认证文件、浏览器资料、原始 Agent 会话和未脱敏客户数据。
- 不把本机绝对路径写成团队必须依赖的运行接口；文档示例优先使用仓库相对路径。
- 对外发布、创建 PR、合并 `main`、删除远端内容或变更仓库可见性前，必须确认用户授权覆盖该动作。
