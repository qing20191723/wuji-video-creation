---
name: seedance-film-production
description: 将创意、小说或剧本推进为短剧剧本、文字分镜、必要资产、宫格分镜图与视频提示词；也可单独做剧本、对白、表演、节奏或声音诊断。
license: proprietary
metadata:
  version: "3.1.0"
  author: "Qingchen + Codex"
  hermes:
    tags: [film-production, narrative-direction, performance]
    related_skills: [imagegen]
---

# 无极影视创作

故事成立、分镜有效、资产准确、生成可控。下游继承上游成果，不重新编故事。

## When to Use

- 完整制作按以下五步推进；单项诊断用 specialist 模式，只交付用户请求的范围。
- 本目录是唯一技能源码；不建立另一套动画状态，不要求看板或修改 Grok Bot。
- 默认止于资产图、宫格分镜图和视频提示词，不自动生成视频、剪辑或发布。

## 流程与四次确认

1. **剧本 / script**：读 [剧本](references/story-drama.md)。交付完整可演正文、实质改编与未决问题，第一次确认这版剧本。
2. **文字分镜 / shot_plan**：读 [导演](references/narrative-direction.md)，按需读 [表演](references/emotion-library.md)、[摄影](references/cinematography.md)、[动作](references/action.md)。按场输出六列表格，第二次确认镜头及大致可拍时长。
3. **必要资产 / assets**：读 [连续性](references/assets-continuity.md)、[资产提示词](references/asset-prompts.md)。复用合适素材，人物先半身定脸，按镜头补必要视图。默认内置 imagegen，生成后实际查看；第三次确认实际图片，提示词随图保存。
4. **宫格分镜图 / storyboard**：读 [宫格](references/storyboard-16grid.md)。提供彩色与黑白线稿两种选项；沿用用户已选样式，未选时在资产审阅时一并询问，不增加确认门禁。有效状态决定格数、短行和分页，镜号映射写在图外。逐格检查后第四次确认实际画板。
5. **视频提示词 / compile**：宫格通过后直接交付。读 [编译](references/seedance-output.md)，指定 Wan 时加读 [适配](references/wan3-output.md)。每单元交付制作信息、真实参考及职责、一段自然语言正文。

默认在四次成果确认处等待用户；阶段内方向明确就继续。定脸和补图同属资产阶段，提示词无需另行审批。用户已有授权不重复询问；自检不冒充用户确认。无必要资产时说明原因，不制作凑数素材。

## 按需读取

[工作流](references/workflow.md) 管理推进与异常；使用工具或迁移时读 [状态协议](references/state-schema.md)。
表演只检索当前冲突相关条目，不加载全部词库；普通短剧不加载专项内容和动画引擎。
对白读 [会诊](references/review-dialogue.md)，节奏读 [节奏](references/platform-rhythm.md)，声音读 [声音](references/post-sound.md)，自然写作读 [去模板化](references/human-writing.md)；特殊内容先读 [边界](references/content-routing.md)，遵循当前执行环境，不按内容自动选择另一模型。

## 状态与真实产物

新项目使用 Schema 2.0 模板。稳定 ID、成果版本和直接依赖形成一个事实源；确认绑定具体成果，全局 revision 只记变更。局部修改只传播到受影响依赖；纯提示词措辞不回退剧本。
旧 1.x 仍走原校验路径。显式迁移另存新文件，保留旧数据和批准证据，不伪造新批准、不伪称画板样式、不要求历史项目全部重做。
中性定脸图不限制情绪强度；线稿只控制构图、位置和状态，彩色资产控制身份、服装、材质、颜色与空间，不把视频变成线稿动画。
图像或工具失败时保存待生成/blocked 状态及问题，不把提示词当作已生成图、不虚构附件。模型限制在编译时按实际入口核验。
