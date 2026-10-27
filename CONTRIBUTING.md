# 协作与分支合并原则

维护者：@qing20191723。适用于人工、GPT、Codex、Grok、Hermes 等所有参与者。2026-10-27 本版覆盖旧文档中“仅某一种智能体可以最终质检”的限制；最终合并由维护者或其明确授权的人决定。

## 先选对基线

| 工作 | PR 目标分支 |
| --- | --- |
| 吴子豪主角家建模、场景机位、空间资产 | `codex/20261014-secret-teaching-home-assets` |
| 影视 Skill 3.2 开发 | `codex/20261003-film-skill-integration` |
| 已稳定的通用说明、仓库协作规则 | `main` |

`main` 不包含建模分支的全部资产。不要把 main 当作主角家模型最新版，也不要为同步顺手将整个建模分支合入 main。专题集成完成后，由维护者另开 PR 决定是否进入 main。

## 一人一任务一分支

1. 先读 `AGENTS.md`、`README.md`、`docs/project-state.md`；建模任务再读 `docs/collaboration/吴子豪主角家建模协作.md`。
2. 查看 Issues、开放 PR 和项目状态，确认目标文件没有其他人正在修改。在 Issue/PR 写明任务、负责人、目标文件及验收办法。GPT 没有发消息授权时先拟好文字交给用户发送。
3. 使用独立 clone/worktree。命名为 `contrib/<GitHub用户名>/<YYYYMMDD>-<主题>`，智能体可以沿用 `codex/`、`grok/`、`hermes/` 前缀；必须包含可区分的任务名。
4. 没有仓库写权限：Fork 后从**对应专题分支**创建个人分支，再向上游同名专题分支发 PR。公开仓库不等于所有人都有直接写权限。
5. 只暂存本任务文件，不覆盖未提交修改，不提交本机路径、个人联系方式、原始聊天、认证文件及缓存。

以建模任务为例（在独立目录执行；已有目录先检查状态）：

```sh
git clone https://github.com/qing20191723/wuji-video-creation.git
cd wuji-video-creation
git lfs install --local
git fetch origin --prune
git switch -c contrib/YOURNAME/YYYYMMDD-home-topic origin/codex/20261014-secret-teaching-home-assets
git lfs pull
git status --short --branch
```

Fork 用户把上游仓库设为 `upstream`，上面基线改用 `upstream/codex/20261014-secret-teaching-home-assets`，推送到自己的 `origin`。LFS 需要安装 Git LFS；下载后确认 `.blend`、`.glb`、图片是实体文件，不能拿指针当模型。跨 fork 的 LFS 上传支持取决于 GitHub；失败时由维护者接收已校验资产，不能假称上传成功。

## 同步、冲突和提交

- 编辑前和提交前 fetch。对照任务的**实际目标分支**同步，禁止固定把 main rebase 到所有建模任务。
- 尚未共享的个人分支可 rebase 到更新后的目标分支；已共享分支使用 merge 或与负责人协商。禁止强推共享分支。
- `.blend`、`.glb`、生成图不能做文本冲突合并。同一模型由单一负责人写入；冲突先比较基线、相机、对象清单与验证结果，再由维护者选择重建方案。
- 先 `git diff --check` 与 `git diff --cached`，再提交；标题用 `feat:`、`fix:`、`docs:`、`chore:`。正文记录负责人/Agent、基线、验证结果。
- 不使用 `reset --hard`、`clean -fd` 或强推来掩盖冲突。不把别人的提交或本机未发布素材混入任务。

## PR 与合并

- PR 必须说明目标分支、具体变化、受影响文件、测试或实际截图、模型/资源版本、未验证项及回退办法。
- 修改代码运行对应测试；修改模型核对坐标、尺寸、连接、相机、LFS 实体及贴图；修改图像必须实际查看，结构测试不能替代视觉验收。
- CI 通过、审查意见解决后，由维护者审核合并。贡献者及其 GPT 不自行合入 main 或共享建模分支。
- 普通小任务优先 squash；需要保留建模版本谱系时由维护者选择 merge commit。
- 合并后更新项目状态和有效资产入口。未通过的图保留“待修/未验证”，不得进入合格清单。

## 公开版本与旧副本

本仓库从私有历史脱敏重建，保留各专题分支。原始 PR 和含本机信息的旧历史只在私有档案库保留。旧提交编号已变化，部分历史验证记录仅代表当时的检查。

协作者应重新 clone 公开仓库；不要 merge、整分支推送或 mirror 旧私有副本，以免带回已清理历史。确有未提交工作时，先保留本地副本，按文件差异迁移到新基线并重新扫描，不直接复制 `.git`。

公开范围包含创作方法、剧情、品牌和场景资料；保留各素材原有来源及许可记录。公开设置本身不替代素材原许可，也不授权改用未知素材许可证。
