# Schema 2.0：一份状态、四次确认

用 assets/project-state.template.json 建项目。运行 `python scripts/validate_project_state.py PROJECT.json`（脚本路径相对技能目录）；2.0 会检查依赖、批准绑定和实际媒体哈希，1.x 原样分派 legacy_project_state.py。
状态工具只提供结构与变更记录，不替代实际图片检查或人的审阅。确认 evidence 必须来自真实用户对当前成果的回复；测试夹具中的合成回复不得用于生产批准。

## 数据约定

根：schema_version、project_id、revision、task_mode、stage、format、source_lock、artifacts、pending_review、approvals、change_log、model_profiles、delivery。specialist_tasks 记录单项诊断，不创建第二份生产状态。
stage 为 script / shot_plan / assets / storyboard / compile。前四阶段分别对应 scene / shot / asset / board；编译有 unit 和 prompt 两类。每项含 id、kind、version、status、content、aspect_versions、depends_on、approved_version。
状态 draft / ready / awaiting_confirmation / approved / stale / blocked。ready 指制作与自检完成，approved 才是用户确认。图片缺失或失败用 blocked，不创建虚假 media。
content 的普通必填字段：scene(heading,text)，shot(size,camera,action,sound,join)，asset(role,description)，unit(duration_seconds,start_state,end_state,join)，prompt(text,profile_id,references)。镜头预计时长可另存 content.duration_seconds，用户仍看六列表格。
asset.content.used_by 列出使用它的镜头 ID，用于外观变更重验；画板和提示词直接依赖资产。资产本身依赖源场或已确认分镜；不要为登记使用而改变已批准镜头正文。
board.content 包含 style（black_white_lineart 或 color）、panel_aspect、row_lengths 和 panels；每格有 id、shot_id、state，直接引用该镜头。跨页用独立 board ID，panel ID 项目内应保持稳定。
样式选择证据保存在 board.content.style_evidence，形式与实际图一致；旧2.0黑白项目无需新增字段即可校验。修改已有画板样式走 visual 变更并重新审阅，只影响该板及其下游，不回退资产、镜头和剧本。
图片 media 必须含 path、sha256、reviewed=true、reviewed_version、review_note；相对路径基于状态文件目录，实际查看后才填写。提示词保存在 content.prompt，已有素材来源存 content.source。
prompt.references 每项包含 id、name（如 @图片1）、role。asset 的 role 为 identity_appearance_space；board 为 composition_action。每个引用同时是直接依赖，且对应实际文件。
model_profiles 每项有 id、model、entry、verified_at、source、supports_combined_refs、limits(duration_seconds,prompt_characters,images)。来源是本轮当前入口或官方文档，不能复制旧参数。未知写 null；不支持所需参考时保留 blocked。入口人像接入、附件方式等未决项写 profile.blockers；存在 blocker 的提示词不能标 ready。

## 版本、依赖与变更

aspect_versions 记录 story / dialogue / performance / visual / timing / sound / wording 七个维度的版本；这是内部变更元数据，不是七份创作表。
depends_on 每项为 {"id":"SC-01","versions":{"story":1,"visual":1}}。默认 dependency(a) 依赖全部维度；只确信用途单一才用 dependency(a,("visual",))。资产身份可以只继承视觉，避免对白变化重做定脸照。
apply_change(state, target_ids, change_type, reason) 返回副本；提高被影响项的 version 和相应维度，按依赖传播并保存旧 approvals。共享资产 visual 变化也经 used_by 传播到镜头。无关成果及批准完全保留，global revision 只作审计。
支持 story（全维度）、dialogue（对白/表演/时长/声音）、performance（表演/视觉/时长）、visual、timing、sound、wording（仅 prompt）。
先 apply_change，再改 stale 项的内容，重做/复用必要产物并人工复核，然后 refresh_dependencies 更新快照；它只转 draft，不自动制作或确认。检查完成才能标 ready。
批准绑定 id/version/digest/aspects，不只绑定 revision；直接改已批准正文会校验失败。未变维度的旧批准可继续证明下游所用事实，已变维度则不行。

## 调用顺序

从脚本目录导入 project_state_v2，使用 new_state / new_artifact / dependency 构建草稿；依剧情生成内容，标 ready 后：
`state = submit_review(state, "script")`，实际用户回复后 `state = approve_pending_gate(state, evidence)`。
分镜同理；资产和画板的两步均传 media_base=状态文件目录，以验证真实文件。不能将自检结论填作 evidence。
编译没有批准函数，unit/prompt 通过验证后标 ready，完整交付设置 delivery.status=ready。读写由调用方显式完成，保留旧状态版本，不覆盖原始素材。
所有 API 返回新状态；操作后再次校验并安全保存。内容发生实质改变须先登记变更，不能通过改 status 绕过依赖。

## 旧项目显式迁移

`python scripts/migrate_project_state.py OLD.json NEW.json` 先走旧校验，仅创建不存在的新文件；拒绝覆盖与原地迁移。
完整原数据进入 legacy_snapshot，保存原始哈希、素材基准目录、全部未知字段和旧批准记录；能识别的成果成为 draft，原 ID 保留，无 ID 的项记录映射。
迁移不是重新创作：历史项目仍可用旧校验继续；只有需进入新流程的成果才补齐新结构，并复用可核验的旧图片和确认依据。工具不自动推断新批准。旧板保留实际风格或 legacy_unspecified，不自动标黑白通过。
