#!/usr/bin/env python3
"""Validate and transition Seedance film project state without external packages."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REF_RE = re.compile(r"^@(图片|视频|音频)([1-9]\d*)$")
STAGE_RE = re.compile(r"^S(?:[0-9]|10)$")
GATE_ORDER = [
    "script_adaptation",
    "shot_breakdown",
    "asset_prompts",
    "character_look",
    "asset_images",
    "storyboard",
    "final_compile",
]
GATE_STATUSES = {
    "pending",
    "awaiting_confirmation",
    "approved",
    "changes_requested",
    "not_required",
}
COMPLETE_GATE_STATUSES = {"approved", "not_required"}
CHARACTER_PANEL_ORDER = [
    "front_half_body_face_closeup",
    "front_full_body",
    "profile_90_full_body",
    "back_full_body",
]
TASK_MODES = {"full_production", "specialist"}
SPECIALIST_TYPES = {"script_review", "dialogue_polish", "platform_rhythm", "post_sound"}
SPECIALIST_STATUSES = {
    "draft",
    "in_progress",
    "awaiting_confirmation",
    "approved",
    "changes_requested",
    "completed",
}
FINDING_PRIORITIES = {"high", "medium", "low"}
PACING_LEVELS = {
    "cinematic_medium",
    "shortform_dense",
    "high_density_hook_action",
    "slow_high_information",
}
ACTION_TYPES = {"free_combat", "wuxia_weapons", "superpower", "battlefield"}
OFFICIAL_LIMITS = {"duration_seconds": 30, "images": 30, "videos": 10, "audios": 10}
REF_LIMIT_KEYS = {"图片": "images", "视频": "videos", "音频": "audios"}
FULL_REAPPROVAL_CHANGES = {"script", "dialogue", "rhythm"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("项目状态根节点必须是对象")
    return data


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _reset_gate(gate: dict[str, Any]) -> None:
    gate["status"] = "pending"
    gate["approved_revision"] = None
    gate["note"] = ""


def apply_change(data: dict[str, Any], change_type: str, reason: str = "") -> None:
    """Apply the deterministic gate invalidation policy in memory.

    This helper does not write a file. Callers decide whether and where to persist.
    """

    if change_type not in FULL_REAPPROVAL_CHANGES | {"post_sound_prompt", "diagnostic"}:
        raise ValueError(f"不支持的 change_type: {change_type}")

    old_revision = data.get("revision")
    if not isinstance(old_revision, int) or old_revision < 1:
        raise ValueError("revision 必须是正整数")

    gates = data.get("approval_gates")
    if not isinstance(gates, dict):
        raise ValueError("缺少 approval_gates")

    new_revision = old_revision
    invalidated: list[str] = []

    if change_type in FULL_REAPPROVAL_CHANGES:
        new_revision += 1
        data["revision"] = new_revision
        data["stage"] = "S1"
        for gate_name in GATE_ORDER:
            gate = gates.get(gate_name)
            if not isinstance(gate, dict):
                gate = {}
                gates[gate_name] = gate
            _reset_gate(gate)
            invalidated.append(gate_name)

        adapted_script = data.get("adapted_script")
        if isinstance(adapted_script, dict):
            adapted_script["status"] = "draft"
            adapted_script["source_revision"] = new_revision
            adapted_script["approved_revision"] = None

        rhythm = data.get("rhythm_profile")
        if isinstance(rhythm, dict):
            rhythm["locked_revision"] = None

    elif change_type == "post_sound_prompt":
        gate = gates.get("final_compile")
        if not isinstance(gate, dict):
            gate = {}
            gates["final_compile"] = gate
        _reset_gate(gate)
        invalidated.append("final_compile")

    interaction = data.get("interaction_state")
    if isinstance(interaction, dict) and change_type != "diagnostic":
        interaction["current_stage"] = "S1" if change_type in FULL_REAPPROVAL_CHANGES else "S9"
        interaction["pending_gate"] = None
        interaction["approval_scope"] = []
        interaction["next_actions"] = ["重新提交受影响阶段并等待确认"]

    log = data.setdefault("change_log", [])
    if not isinstance(log, list):
        raise ValueError("change_log 必须是数组")
    log.append(
        {
            "change_type": change_type,
            "reason": reason,
            "old_revision": old_revision,
            "new_revision": new_revision,
            "invalidated_gates": invalidated,
            "applied_at": _timestamp(),
        }
    )


def approve_pending_gate(data: dict[str, Any]) -> str:
    """Approve exactly one awaiting gate and return its name."""

    gates = data.get("approval_gates")
    if not isinstance(gates, dict):
        raise ValueError("缺少 approval_gates")
    awaiting = [
        name
        for name in GATE_ORDER
        if isinstance(gates.get(name), dict)
        and gates[name].get("status") == "awaiting_confirmation"
    ]
    if len(awaiting) != 1:
        raise ValueError(f"必须且只能有一个等待确认门禁，实际为 {len(awaiting)}")

    gate_name = awaiting[0]
    interaction = data.get("interaction_state")
    if isinstance(interaction, dict):
        declared = interaction.get("pending_gate")
        if declared not in {None, gate_name}:
            raise ValueError(f"交互状态等待 {declared}，实际等待 {gate_name}")

    gates[gate_name]["status"] = "approved"
    gates[gate_name]["approved_revision"] = data.get("revision")
    if isinstance(interaction, dict):
        interaction["pending_gate"] = None
        interaction["approval_scope"] = []
    return gate_name


def _require_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{field} 必须是数组")
        return []
    return value


def _validate_v12(data: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    task_mode = data.get("task_mode")
    if task_mode not in TASK_MODES:
        errors.append(f"task_mode 必须为 full_production 或 specialist，实际为 {task_mode}")

    stage = data.get("stage")
    if not isinstance(stage, str) or not STAGE_RE.match(stage):
        errors.append(f"stage 必须为 S0–S10，实际为 {stage}")

    interaction = data.get("interaction_state")
    if not isinstance(interaction, dict):
        errors.append("缺少 interaction_state")
        interaction = {}
    current_stage = interaction.get("current_stage")
    if current_stage != "specialist" and (
        not isinstance(current_stage, str) or not STAGE_RE.match(current_stage)
    ):
        errors.append("interaction_state.current_stage 必须为 S0–S10 或 specialist")
    pending_gate = interaction.get("pending_gate")
    if pending_gate is not None and pending_gate not in GATE_ORDER:
        errors.append(f"interaction_state.pending_gate 无效: {pending_gate}")
    for field in ("approval_scope", "blockers", "next_actions"):
        _require_list(interaction.get(field), f"interaction_state.{field}", errors)

    model = data.get("model_profile")
    if not isinstance(model, dict):
        errors.append("缺少 model_profile")
        model = {}
    if model.get("model") != "seedance-2.5":
        errors.append("model_profile.model 必须为 seedance-2.5")
    official = model.get("official_limits")
    if official != OFFICIAL_LIMITS:
        errors.append("model_profile.official_limits 必须保持官方 30秒/30图/10视频/10音频上限")
    effective = model.get("effective_limits")
    if not isinstance(effective, dict):
        errors.append("缺少 model_profile.effective_limits")
        effective = OFFICIAL_LIMITS
    for key, official_max in OFFICIAL_LIMITS.items():
        value = effective.get(key)
        if not isinstance(value, int) or value < 1 or value > official_max:
            errors.append(f"effective_limits.{key} 必须为 1–{official_max} 的整数")
    if not isinstance(model.get("verified_source"), str) or not model.get("verified_source"):
        errors.append("model_profile 缺少 verified_source")

    rhythm = data.get("rhythm_profile")
    if not isinstance(rhythm, dict):
        errors.append("缺少 rhythm_profile")
        rhythm = {}
    if rhythm.get("pacing") not in PACING_LEVELS:
        errors.append(f"rhythm_profile.pacing 无效: {rhythm.get('pacing')}")
    if not isinstance(rhythm.get("platform"), str) or not rhythm.get("platform"):
        errors.append("rhythm_profile.platform 必须是非空字符串")
    if not isinstance(rhythm.get("duration_tier"), str) or not rhythm.get("duration_tier"):
        errors.append("rhythm_profile.duration_tier 必须是非空字符串")
    hook = rhythm.get("hook_window_seconds")
    if (
        not isinstance(hook, list)
        or len(hook) != 2
        or not all(isinstance(item, (int, float)) for item in hook)
        or hook[0] < 0
        or hook[1] <= hook[0]
    ):
        errors.append("rhythm_profile.hook_window_seconds 必须是递增的两个非负数字")
    interval = rhythm.get("progression_interval_seconds")
    if not isinstance(interval, int) or interval < 1:
        errors.append("rhythm_profile.progression_interval_seconds 必须是正整数")
    if rhythm.get("breathing_shot_rule") != "function_required":
        errors.append("rhythm_profile.breathing_shot_rule 必须为 function_required")
    locked_revision = rhythm.get("locked_revision")
    if locked_revision is not None and locked_revision != data.get("revision"):
        errors.append("rhythm_profile.locked_revision 与当前 revision 不一致")

    characters = _require_list(data.get("characters"), "characters", errors)
    for index, character in enumerate(characters):
        if not isinstance(character, dict):
            errors.append(f"characters[{index}] 必须是对象")
            continue
        if not character.get("id"):
            errors.append(f"characters[{index}] 缺少 id")
        voiceprint = character.get("voiceprint")
        if voiceprint is None:
            continue
        if not isinstance(voiceprint, dict):
            errors.append(f"角色 {character.get('id')} 的 voiceprint 必须是对象")
            continue
        for field in ("vocabulary", "syntax", "forbidden_terms"):
            _require_list(voiceprint.get(field), f"角色 {character.get('id')} voiceprint.{field}", errors)
        for field in ("sentence_length", "era_register"):
            if not isinstance(voiceprint.get(field), str) or not voiceprint.get(field):
                errors.append(f"角色 {character.get('id')} voiceprint.{field} 必须是非空字符串")

    tasks = _require_list(data.get("specialist_tasks"), "specialist_tasks", errors)
    if task_mode == "specialist" and not tasks:
        errors.append("specialist 模式至少需要一个 specialist_task")
    task_ids: list[str] = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"specialist_tasks[{index}] 必须是对象")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"specialist_tasks[{index}] 缺少 id")
        else:
            task_ids.append(task_id)
        task_type = task.get("type")
        if task_type not in SPECIALIST_TYPES:
            errors.append(f"专科任务 {task_id} type 无效: {task_type}")
        if task.get("status") not in SPECIALIST_STATUSES:
            errors.append(f"专科任务 {task_id} status 无效: {task.get('status')}")
        if task.get("source_revision") != data.get("revision"):
            errors.append(f"专科任务 {task_id} source_revision 与项目不一致")
        _require_list(task.get("target_ids"), f"专科任务 {task_id} target_ids", errors)
        if not isinstance(task.get("diagnostic_only"), bool):
            errors.append(f"专科任务 {task_id} diagnostic_only 必须是布尔值")
        findings = _require_list(task.get("findings"), f"专科任务 {task_id} findings", errors)
        for finding_index, finding in enumerate(findings):
            if not isinstance(finding, dict):
                errors.append(f"专科任务 {task_id} finding[{finding_index}] 必须是对象")
                continue
            if finding.get("priority") not in FINDING_PRIORITIES:
                errors.append(f"专科任务 {task_id} finding[{finding_index}] priority 无效")
            for field in ("evidence", "impact", "recommendation"):
                if not isinstance(finding.get(field), str) or not finding.get(field).strip():
                    errors.append(f"专科任务 {task_id} finding[{finding_index}] 缺少 {field}")

        if task_type == "dialogue_polish":
            risk = task.get("natural_speech_risk")
            if risk not in {"low", "medium", "high"}:
                errors.append(f"对白任务 {task_id} natural_speech_risk 必须为 low/medium/high")

        if task_type == "post_sound":
            output_layer = task.get("output_layer")
            if output_layer not in {"post_production", "seedance_sound_revision"}:
                errors.append(f"声音任务 {task_id} output_layer 无效")
            writes_to_prompt = task.get("writes_to_seedance_prompt")
            if not isinstance(writes_to_prompt, bool):
                errors.append(f"声音任务 {task_id} writes_to_seedance_prompt 必须是布尔值")
            if output_layer == "post_production" and writes_to_prompt:
                errors.append(f"声音任务 {task_id} 的后期BGM不得写入纯Seedance提示词")
            if output_layer == "seedance_sound_revision":
                final_gate = data.get("approval_gates", {}).get("final_compile", {})
                if final_gate.get("status") == "approved":
                    errors.append(f"声音任务 {task_id} 修改Seedance声音时必须重新打开 final_compile")
            cue_sheet = _require_list(task.get("cue_sheet"), f"声音任务 {task_id} cue_sheet", errors)
            if task.get("mode") == "cue_sheet" and task.get("status") in {"approved", "completed"} and not cue_sheet:
                errors.append(f"声音任务 {task_id} 已完成但缺少 Cue Sheet")
            for cue_index, cue in enumerate(cue_sheet):
                if not isinstance(cue, dict):
                    errors.append(f"声音任务 {task_id} cue[{cue_index}] 必须是对象")
                    continue
                for field in (
                    "timecode",
                    "story_function",
                    "entry_exit",
                    "dialogue_ducking",
                    "silence",
                    "licensing_note",
                ):
                    if not isinstance(cue.get(field), str) or not cue.get(field).strip():
                        errors.append(f"声音任务 {task_id} cue[{cue_index}] 缺少 {field}")
    if len(task_ids) != len(set(task_ids)):
        errors.append("specialist_tasks id 重复")


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    schema_version = data.get("schema_version")
    if schema_version not in {"1.1", "1.2"}:
        errors.append("schema_version 必须为 1.1 或 1.2")
    elif schema_version == "1.1":
        warnings.append("schema_version 1.1 为兼容格式；建议升级到 1.2 以使用专科、节奏和模型配置校验")
    else:
        _validate_v12(data, errors, warnings)

    if not data.get("project_id"):
        errors.append("缺少 project_id")
    if not isinstance(data.get("revision"), int) or data.get("revision", 0) < 1:
        errors.append("revision 必须是正整数")

    production_rules = data.get("production_rules")
    if not isinstance(production_rules, dict):
        errors.append("缺少 production_rules")
        production_rules = {}
    if production_rules.get("drama_segment_seconds") != 30:
        errors.append("文戏单元必须固定为30秒")
    if production_rules.get("action_segment_seconds") != 25:
        errors.append("武戏单元必须固定为25秒")
    character_rule = production_rules.get("character_identity_asset")
    if not isinstance(character_rule, dict):
        errors.append("缺少 character_identity_asset 规则")
        character_rule = {}
    if character_rule.get("layout") != "single_horizontal_four_panel":
        errors.append("人物定妆资产必须使用同画布横向四栏格式")
    if character_rule.get("panel_order") != CHARACTER_PANEL_ORDER:
        errors.append("人物定妆四栏顺序必须为正面半身、全身正面、90度侧面、全身背面")
    if character_rule.get("pose") != "natural_neutral_standing":
        errors.append("人物定妆姿态必须为自然中性站立")
    if character_rule.get("front_view_gaze") != "head_face_eyes_straight_to_camera":
        errors.append("正面半身与全身正面必须头部、面部和双眼正对镜头")
    if character_rule.get("full_body_alignment") != "same_height_same_foot_baseline":
        errors.append("三个全身栏位必须等高且脚底同基线")

    gates = data.get("approval_gates")
    if not isinstance(gates, dict):
        errors.append("缺少 approval_gates")
        gates = {}
    seen_unapproved = False
    awaiting: list[str] = []
    for gate_name in GATE_ORDER:
        gate = gates.get(gate_name)
        if not isinstance(gate, dict):
            errors.append(f"缺少确认门禁 {gate_name}")
            seen_unapproved = True
            continue
        status = gate.get("status")
        if status not in GATE_STATUSES:
            errors.append(f"门禁 {gate_name} 状态无效: {status}")
        if status == "awaiting_confirmation":
            awaiting.append(gate_name)
        is_complete = status in COMPLETE_GATE_STATUSES
        if is_complete and seen_unapproved:
            errors.append(f"门禁 {gate_name} 已完成，但上游门禁尚未批准")
        if not is_complete:
            seen_unapproved = True
        if status == "approved" and gate.get("approved_revision") != data.get("revision"):
            errors.append(f"门禁 {gate_name} 批准revision与当前项目不一致")
    if len(awaiting) > 1:
        errors.append("同时等待确认的核心门禁不得超过一个")

    if schema_version == "1.2":
        interaction = data.get("interaction_state", {})
        declared = interaction.get("pending_gate") if isinstance(interaction, dict) else None
        actual = awaiting[0] if len(awaiting) == 1 else None
        if declared != actual:
            errors.append(f"interaction_state.pending_gate 为 {declared}，实际等待门禁为 {actual}")

    adapted_script = data.get("adapted_script")
    if not isinstance(adapted_script, dict):
        errors.append("缺少 adapted_script")
        adapted_script = {}
    if adapted_script.get("source_revision") != data.get("revision"):
        errors.append("adapted_script 的 source_revision 与当前项目不一致")
    if gates.get("script_adaptation", {}).get("status") == "approved":
        if adapted_script.get("status") != "approved":
            errors.append("剧本优化门禁已批准，但 adapted_script 未标记 approved")
        if adapted_script.get("approved_revision") != data.get("revision"):
            errors.append("adapted_script 批准revision与当前项目不一致")
        scene_ids = adapted_script.get("scene_ids")
        if not isinstance(scene_ids, list) or not scene_ids:
            errors.append("AI可生成剧本已批准，但缺少场次ID")
        elif len(scene_ids) != len(set(scene_ids)):
            errors.append("AI可生成剧本场次ID重复")

    assets = data.get("assets", [])
    if not isinstance(assets, list):
        errors.append("assets 必须是数组")
        assets = []
    asset_ids = [item.get("id") for item in assets if isinstance(item, dict)]
    if len(asset_ids) != len(assets):
        errors.append("assets 中存在非对象条目")
    if None in asset_ids or "" in asset_ids:
        errors.append("存在缺少 id 的资产")
    if len(asset_ids) != len(set(asset_ids)):
        errors.append("资产 id 重复")

    attachment_refs: list[str] = []
    ref_counts = {"images": set(), "videos": set(), "audios": set()}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        ref = asset.get("attachment_ref")
        status = asset.get("status", "planned")
        if ref:
            match = REF_RE.match(ref) if isinstance(ref, str) else None
            if not match:
                errors.append(f"资产 {asset.get('id')} 的 attachment_ref 格式无效: {ref}")
            else:
                attachment_refs.append(ref)
                ref_counts[REF_LIMIT_KEYS[match.group(1)]].add(ref)
        if ref and status != "approved":
            errors.append(f"资产 {asset.get('id')} 未 approved 却绑定了正式引用 {ref}")
        if ref and gates.get("asset_images", {}).get("status") != "approved":
            errors.append(f"资产 {asset.get('id')} 在资产图门禁批准前绑定了正式引用 {ref}")
        if status == "approved" and not asset.get("responsibility"):
            errors.append(f"资产 {asset.get('id')} 已 approved 但缺少 responsibility")
    if len(attachment_refs) != len(set(attachment_refs)):
        errors.append("同一正式附件引用绑定了多个资产职责")

    effective_limits = OFFICIAL_LIMITS
    if schema_version == "1.2":
        candidate = data.get("model_profile", {}).get("effective_limits")
        if isinstance(candidate, dict):
            effective_limits = {**OFFICIAL_LIMITS, **candidate}
    for kind in ("images", "videos", "audios"):
        count = len(ref_counts[kind])
        limit = effective_limits.get(kind, OFFICIAL_LIMITS[kind])
        if isinstance(limit, int) and count > limit:
            errors.append(f"正式{kind}引用数量 {count} 超过有效上限 {limit}")

    segments = data.get("segments", [])
    if not isinstance(segments, list):
        errors.append("segments 必须是数组")
        segments = []
    if segments and gates.get("script_adaptation", {}).get("status") not in COMPLETE_GATE_STATUSES:
        errors.append("AI可生成剧本尚未确认，不得建立分段或连续分镜")
    if gates.get("shot_breakdown", {}).get("status") == "approved" and not segments:
        errors.append("连续分镜门禁已批准，但项目没有任何分段")
    if assets and gates.get("shot_breakdown", {}).get("status") not in COMPLETE_GATE_STATUSES:
        errors.append("连续分镜尚未确认，不得建立正式资产清单")
    segment_ids = [item.get("id") for item in segments if isinstance(item, dict)]
    if len(segment_ids) != len(segments):
        errors.append("segments 中存在非对象条目")
    if len(segment_ids) != len(set(segment_ids)):
        errors.append("片段 id 重复")

    project_pacing = data.get("rhythm_profile", {}).get("pacing")
    previous_end_state = None
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        sid = segment.get("id", "<unknown>")
        mode = segment.get("mode")
        duration = segment.get("duration_seconds")
        shots = segment.get("shots", [])

        expected_duration = 30 if mode == "drama" else 25 if mode == "action" else None
        if expected_duration is None:
            errors.append(f"片段 {sid} 的 mode 必须为 drama 或 action")
            continue
        if duration != expected_duration:
            errors.append(f"片段 {sid} 时长应为 {expected_duration} 秒，实际为 {duration}")
        if not isinstance(shots, list):
            errors.append(f"片段 {sid} shots 必须是数组")
            shots = []

        shot_count = len(shots)
        if mode == "drama" and not 16 <= shot_count <= 22:
            errors.append(f"文戏片段 {sid} 应有 16–22 镜，实际为 {shot_count}")
        if mode == "action" and shot_count != 16:
            errors.append(f"武戏片段 {sid} 应严格16镜，实际为 {shot_count}")

        if schema_version == "1.2":
            pacing = segment.get("rhythm_pacing", project_pacing)
            if pacing not in PACING_LEVELS:
                errors.append(f"片段 {sid} rhythm_pacing 无效: {pacing}")
            if pacing != project_pacing and not segment.get("rhythm_exception_reason"):
                errors.append(f"片段 {sid} 偏离项目节奏档位但缺少 rhythm_exception_reason")
            action_types = segment.get("action_types", [])
            if not isinstance(action_types, list):
                errors.append(f"片段 {sid} action_types 必须是数组")
                action_types = []
            if len(action_types) > 2:
                errors.append(f"片段 {sid} 混合动作类型最多两个")
            invalid_action_types = set(action_types) - ACTION_TYPES
            if invalid_action_types:
                errors.append(f"片段 {sid} 存在无效动作类型: {sorted(invalid_action_types)}")
            if mode != "action" and action_types:
                warnings.append(f"文戏片段 {sid} 配置了动作类型，请确认确有需要")

        expected_number = 1
        expected_start = 0.0
        for shot in shots:
            if not isinstance(shot, dict):
                errors.append(f"片段 {sid} 存在非对象镜头")
                continue
            number = shot.get("number")
            start = shot.get("start")
            end = shot.get("end")
            if number != expected_number:
                errors.append(f"片段 {sid} 镜头编号应为 {expected_number}，实际为 {number}")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                errors.append(f"片段 {sid} 镜头 {number} 的时间必须为数字")
            else:
                if abs(float(start) - expected_start) > 0.001:
                    errors.append(f"片段 {sid} 镜头 {number} 起点不连续: {start}，期望 {expected_start}")
                if end <= start:
                    errors.append(f"片段 {sid} 镜头 {number} 终点必须大于起点")
                expected_start = float(end)
            for asset_id in shot.get("asset_ids", []):
                if asset_id not in asset_ids:
                    errors.append(f"片段 {sid} 镜头 {number} 引用了不存在的资产 {asset_id}")
            expected_number += 1

        if shots and abs(expected_start - expected_duration) > 0.001:
            errors.append(f"片段 {sid} 末点应为 {expected_duration} 秒，实际为 {expected_start}")

        start_state = segment.get("start_state")
        end_state = segment.get("end_state")
        if not start_state:
            errors.append(f"片段 {sid} 缺少 start_state")
        if not end_state:
            errors.append(f"片段 {sid} 缺少 end_state")
        if previous_end_state is not None and start_state != previous_end_state:
            warnings.append(f"片段 {sid} 的 start_state 与上一段 end_state 不完全一致，请人工核对")
        previous_end_state = end_state

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: validate_project_state.py <project-state.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        data = load(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"读取失败: {exc}")
        return 2

    errors, warnings = validate(data)
    for item in warnings:
        print(f"警告: {item}")
    for item in errors:
        print(f"错误: {item}")
    if errors:
        print(f"校验失败: {len(errors)} 个错误，{len(warnings)} 个警告")
        return 1
    print(f"校验通过: 0 个错误，{len(warnings)} 个警告")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
