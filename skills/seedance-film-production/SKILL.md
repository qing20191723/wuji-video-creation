---
name: seedance-film-production
description: 将剧本与多模态参考推进为可追溯的双模型影视生产包，或单独诊断剧本、对白、表演、节奏和声音。
license: proprietary
metadata:
  version: "1.8.0"
  author: "Qingchen + Codex"
  hermes:
    tags: [film-production, seedance, wan, narrative-direction, performance]
    related_skills: [imagegen]
---

# Seedance 影视创作流水线

把每个生成片段当成一个叙事段落：先让这一层故事意思成立并结束，再从新的观看位置进入下一层；继承故事世界，不机械延长上一台摄影机。镜头数、片长、宫格和模型上限都不能反推剧情。

## When to Use

- `full_production`：把想法、小说、剧本或参考素材推进为剧本、分镜、资产、正常段十六宫格及 Seedance 2.5 / Wan 3.0 音画一体提示词。
- `specialist`：只做剧本会诊、对白精修、表演设计、平台节奏或后期声音。不要因用户贴出剧本就自动启动全流程。
- 不用于团队协作表、普通影视知识问答或单图润色。G1–G7 只锁创作产物，不替代负责人、审核、发布与交付表。

## 硬约束

1. 用户确认内容、原始素材与批准边界是 Canon；下游只读取当前 revision 的批准产物。
2. 稳定 ID、版本、来源跨度和真实附件必须可追溯。未验收附件不能写成 `@图片N/@视频N/@音频N`。
3. 最终编译只转换已批准内容，不新增剧情、人物、道具、行为、台词或结局。
4. 正常跨度只进入 Seedance 2.5；成人跨度只进入 Wan 3.0；每个跨度有且只有一个路由。
5. 两路均原生音画一体。片长按实际可拍内容估算，不填满 30 秒，不设镜头配额。
6. 正常完整生产使用 4×4 十六宫格做视觉锁定；成人段不做十六宫格。
7. 成人内容仅处理清楚成年、成人化呈现、虚构或获授权且持续自愿的参与者；边界不清时停止询问。禁止未成年人/幼态校园化、真实第三方或公众人物性化、非自愿或失能、偷拍泄露、乱伦、人口剥削、兽交、恋尸及审核规避。
8. 已批准且可处理的成人跨度不能静默删除、概括或升级；当前环境不能展开的细部保留中性行为类别与来源跨度。
9. Wan 3.0 官方提示词上限 20,000 字符；Seedance 2.5 官方未公布字符上限。记录当前入口限制，超限时压缩或在真实叙事段落处拆分，不截断。
10. 自检不等于用户确认；改变 Canon 时写变更记录并按影响范围回退门禁。

## 创作主轴

G1 后的所有分段、摄影和提示词先读取 [叙事段落与镜头再入场](references/narrative-direction.md)。它是以下规则的唯一创作事实源：

- 一个片段只承担一层明确意义，不强制完整起承转合；意义已经被读懂且继续拍只会重复时结束。
- 下一片段从人物、动作、结果、物体、空间或声音重新入场，迅速说明“仍在何处、谁仍在场、继承了什么、现在开始什么”。
- 必须继承人物、环境、身体、服装、道具、情绪、行为结果和下一步因果；摄影机位置、景别、焦点和运动可以重新选择。
- 摄影变化由人物或环境事件引发，并让观众获得新的故事理解；术语本身不是理由。
- 最终提示词像一段具体的影视叙述，从环境中的人物和动作开始，让摄影随注意力自然出现。

## 完整生产门禁

1. `G1 script_adaptation`：锁来源与正常/成人跨度，交付完整可生成剧本和假设，等待确认。
2. `G2 shot_breakdown`：按叙事段落估时，建立表演、再入场、镜头/光影与跨段状态，等待确认。
3. `G3 asset_prompts`：交付稳定资产清单和自然语言提示词，等待确认。
4. `G4 character_look`：生成并验收每名主要角色的横向四栏定妆母版。
5. `G5 asset_images`：分批生成并实际查看场景、道具、VFX 和所需状态资产。
6. `G6 storyboard`：仅为正常路生成并验收十六宫格；成人路为 `not_required`。
7. `G7 final_compile`：逐叙事段落编译 Seedance/Wan 自然语言音画提示词，登记引用、字符数与 revision。

除非用户明确放弃中途确认，否则每次只推进当前唯一门禁。完整步骤、状态卡和回退读取 [工作流](references/workflow.md)。

## 按阶段读取

- G1 剧本：读取 [story-drama.md](references/story-drama.md)；混合内容加读 [content-routing.md](references/content-routing.md)，成人边界加读 [adult-intimacy.md](references/adult-intimacy.md)。
- G2 分镜：读取 [narrative-direction.md](references/narrative-direction.md)；按需加读 [cinematography.md](references/cinematography.md)、[emotion-library.md](references/emotion-library.md)、[action.md](references/action.md) 或 [adult-choreography.md](references/adult-choreography.md)。
- G3–G5 资产：读取 [assets-continuity.md](references/assets-continuity.md) 与 [asset-prompts.md](references/asset-prompts.md)。
- G6 正常故事板：只加读 [storyboard-16grid.md](references/storyboard-16grid.md)。
- G7 编译：正常段读 [seedance-output.md](references/seedance-output.md)，成人段读 [wan3-output.md](references/wan3-output.md)；一次只加载当前模型。
- 写剧本、分镜或提示词需要删模板痕迹时读 [human-writing.md](references/human-writing.md)。

专科入口：剧本/对白读 [review-dialogue.md](references/review-dialogue.md)，表演读叙事导演与情绪库，节奏读 [platform-rhythm.md](references/platform-rhythm.md)，后期声音读 [post-sound.md](references/post-sound.md)。只读诊断不改变 Canon，也不创建无关资产。

## 状态与回退

从 `assets/project-state.template.json` 建立状态。Schema 1.7 的片段以 `narrative_paragraph` 说明本段意义、发展、完成信号和前向冲动，以 `reentry_plan` 说明入场锚点、首个新动作、继承状态和第一条新信息；`camera_plan` 只记录入场观看、注意力推进、真正改变理解的视点变化和结束观看。`transition_ledger` 移交已完成意义、前向冲动、再入场锚点和故事状态，而不是要求摄影机连续。

- 应用剧本、对白、节奏或成人边界变化：提升 revision，回退 G1–G7。
- 改变表演、叙事分段、再入场、镜头、光影或跨段 Canon：保留 G1，回退 G2–G7。
- 修改资产：提升资产版本，回退相应资产门禁并重验引用。
- 只改最终提示词措辞或模型内声音表达：回退 G7。

状态未知时写“未知/待确认/待生成”，不补造。最终运行项目状态、Skill 结构和引用校验；机械通过只证明结构与事实一致，叙事完成度和摄影意义仍须人工复核。
