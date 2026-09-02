---
name: seedance-film-production
description: 将想法、剧本与多模态参考推进为可追溯、可独立生成并可直接切接的 Seedance 2.5 / Wan 3.0 影视生产包，或单独诊断剧本、对白、表演、节奏和声音。
license: proprietary
metadata:
  version: "2.0.0"
  author: "Qingchen + Codex"
  hermes:
    tags: [film-production, seedance, wan, narrative-direction, performance]
    related_skills: [imagegen]
---

# Seedance 影视创作流水线

先讲清故事，再选择观众从哪里看。每个生成单元完成一层可辨认的故事意义；下一单元从新的专业观看位置进入同一世界，继承已发生的一切，而非机械延长上一台摄影机。顺序直拼成立是这种叙事设计的结果。

## When to Use

- `full_production`：交付剧本包、导演分镜包、资产包和模型编译包。
- `specialist`：只做剧本会诊、对白精修、表演设计、平台节奏或后期声音；不要因用户贴出剧本就自动跑完整流程。
- 不用于团队协作表、普通影视知识问答或单图润色。G1–G7 只确认创作产物，不替代人员、审核、发布和交付管理。

## 硬约束

1. 用户确认内容、原始素材和批准边界是 Canon；下游只读取当前 revision 的批准产物。
2. 稳定 ID、版本、来源跨度和真实附件可追溯；未验收附件不能伪装为 `@图片N/@视频N/@音频N`。
3. 最终编译不新增剧情、人物、道具、行为、台词或结局；正常跨度只进 Seedance 2.5，成人跨度只进 Wan 3.0。
4. 两路默认原生音画一体。片长由实际可拍内容决定，不填满 30 秒，不设镜头配额。
5. 正常完整生产默认以 4×4 十六宫格锁视觉；若相关批准内容仍不足 16 个有因果价值的状态，G6 可写明理由后记为 `not_required`。成人段不做宫格。
6. 成人内容只处理明确成年、成人化呈现、虚构或获授权且持续自愿的参与者；边界不清时停在必要询问。禁止未成年人/幼态校园化、真实第三方或公众人物性化、非自愿或失能、偷拍泄露、乱伦、人口剥削、兽交、恋尸及审核规避。
7. 可处理的成人跨度不静默删除、概括或升级；无法展开的细部保留中性行为类别和来源跨度。
8. Wan 3.0 官方提示词上限 20,000 字符；Seedance 2.5 官方未公布字符上限。记录当前入口限制，超限时压缩或在真实叙事边界拆分，禁止截断。
9. 自检不等于用户确认；改变 Canon 时记录影响并按门禁回退。

## 四个生产包与门禁

1. `剧本包（G1）`：锁来源和路由，把文学材料写成没有镜号、资产或模型参数的可演场景稿。读取 [剧本](references/story-drama.md)；混合内容加读 [路由](references/content-routing.md)，成人边界加读 [亲密边界](references/adult-intimacy.md)。
2. `导演分镜包（G2）`：先设计承载主要剧情的观看位置，再补真正带来揭示、反应、悬念、强调或空间重建的视点。读取 [叙事导演](references/narrative-direction.md)，按需加读 [摄影连续](references/cinematography.md)、[表演](references/emotion-library.md)、[动作](references/action.md) 或 [成人编排](references/adult-choreography.md)。
3. `资产包（G3–G6）`：G3 资产提示词，G4 人物四栏母版，G5 场景/道具/状态资产，G6 正常十六宫格。读取 [连续性](references/assets-continuity.md)、[资产提示词](references/asset-prompts.md)，G6 加读 [十六宫格](references/storyboard-16grid.md)。
4. `模型编译包（G7）`：逐叙事段落输出外部制作卡和一段自然导演稿；正常读 [Seedance](references/seedance-output.md)，成人读 [Wan](references/wan3-output.md)，一次只加载当前模型。

除非用户明确放弃中途确认，每次只推进一个门禁。阶段交付、状态卡与回退读 [工作流](references/workflow.md)。删 AI 套话时读 [去模板化](references/human-writing.md)；剧本/对白专科读 [会诊](references/review-dialogue.md)，节奏读 [平台节奏](references/platform-rhythm.md)，后期声音读 [声音](references/post-sound.md)。

## 创作与状态

[叙事导演](references/narrative-direction.md) 是分段、观看设计、再入场、蒙太奇关系和自然视频提示词的唯一创作事实源。结构台账可以用字段，剧本正文和模型正文不能把字段、镜头名词或模块清单当成成品。

从 `assets/project-state.template.json` 建立 Schema 1.9 状态。它保留叙事段落、再入场、表演与光影；使用精简 `composition_plan`、条件式 `camera_plan.continuity`、全局 `sound_bible` 和 `transition_ledger.assembly_contract`。兼容读取 1.1–1.8 并提示升级。

- 剧情、对白、节奏、路由或亲密边界变化：提升 revision，回退 G1–G7。
- 叙事分段、表演、摄影、光影或接合变化：保留 G1，回退 G2–G7。
- 资产变化：提升资产版本，回退相应资产门禁并重验引用。
- 只改最终措辞或模型内声音表达：回退 G7。

未知事实写“未知/待确认/待生成”，不补造。最终运行项目状态、Skill 结构、引用、体量和完整测试；机械通过只证明结构一致，Codex 仍需人工复核剧本是否像人写、每次换镜是否增加理解、各单元直拼后因果与声音是否成立。
