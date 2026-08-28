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
MODULAR_PROMPT_START_RE = re.compile(
    r"^\s*(?:(?:【?(?:镜头|景别|运镜|摄影|灯光|主体|动作|声音)】?\s*[:：])|(?:\d+(?:\.\d+)?\s*秒\s*[,，]))"
)
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
CONTENT_MODES = {"general", "adult_intimacy"}
CONTENT_LANES = {"normal", "adult"}
LANE_TARGET_MODELS = {"normal": "seedance-2.5", "adult": "wan3.0"}
PROMPT_TARGET_MODELS = {"seedance-2.5", "wan3.0"}
INTIMACY_LEVELS = {
    "romantic",
    "sensual",
    "implied_intimacy",
    "non_explicit_nudity",
    "explicit_adult",
}
SOURCE_AUTHORIZATIONS = {"fictional", "verified_self_or_authorized_adult"}
SPECIALIST_TYPES = {
    "script_review",
    "dialogue_polish",
    "performance_design",
    "platform_rhythm",
    "post_sound",
}
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
WAN_OFFICIAL_LIMITS = {
    "duration_seconds": 30,
    "images": 10,
    "videos": 5,
    "video_total_seconds": 15,
    "audios": 5,
    "audio_total_seconds": 15,
    "multimodal_assets": 20,
}
WAN_PROMPT_MAX_CHARACTERS = 20000
REF_LIMIT_KEYS = {"图片": "images", "视频": "videos", "音频": "audios"}
FULL_REAPPROVAL_CHANGES = {
    "script",
    "dialogue",
    "rhythm",
    "content_routing",
    "intimacy_boundary",
}
SHOT_REAPPROVAL_CHANGES = {
    "performance",
    "cinematography",
    "lighting",
    "transition",
}
PERFORMANCE_TRACKS = {
    "gaze",
    "face",
    "head_shoulders",
    "hands_objects",
    "body_weight",
    "breathing_sound",
}
PERFORMANCE_INTENSITIES = {"subtle", "restrained", "clear", "explosive"}
BRIDGE_TYPES = {
    "continuous_action",
    "match_on_action",
    "sound_bridge",
    "occlusion_reveal",
    "graphic_light_match",
    "threshold_blocking",
    "temporal_ellipsis",
}
LANE_CHANGES = {"same_lane", "normal_to_adult", "adult_to_normal"}
HANDOFF_MODES = {"shared_boundary_keyframe", "state_only"}
INTIMACY_ACTION_FAMILIES = {
    "approach_confirmation",
    "kissing_caressing",
    "coverage_change",
    "manual_or_oral",
    "self_stimulation",
    "intercourse",
    "position_support_transition",
    "pause_stop_reconfirm",
    "completion_aftercare",
}
COLLABORATION_ONLY_FIELDS = {
    "collaboration_sheet",
    "google_sheet",
    "review_assignees",
    "feedback_rollup",
    "cloud_review_status",
    "watermarked_delivery",
    "publishing_status",
}


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

    if change_type not in FULL_REAPPROVAL_CHANGES | SHOT_REAPPROVAL_CHANGES | {
        "post_sound_prompt",
        "diagnostic",
    }:
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

        profile = data.get("content_profile")
        intimacy = profile.get("intimacy") if isinstance(profile, dict) else None
        if isinstance(intimacy, dict):
            intimacy["locked_revision"] = None

    elif change_type in SHOT_REAPPROVAL_CHANGES:
        new_revision += 1
        data["revision"] = new_revision
        data["stage"] = "S3"

        script_gate = gates.get("script_adaptation")
        if isinstance(script_gate, dict) and script_gate.get("status") == "approved":
            script_gate["approved_revision"] = new_revision

        adapted_script = data.get("adapted_script")
        if isinstance(adapted_script, dict):
            adapted_script["source_revision"] = new_revision
            if adapted_script.get("status") == "approved":
                adapted_script["approved_revision"] = new_revision

        for gate_name in GATE_ORDER[1:]:
            gate = gates.get(gate_name)
            if not isinstance(gate, dict):
                gate = {}
                gates[gate_name] = gate
            _reset_gate(gate)
            invalidated.append(gate_name)

        visual_bible = data.get("visual_bible")
        lighting = visual_bible.get("lighting") if isinstance(visual_bible, dict) else None
        if isinstance(lighting, dict):
            lighting["locked_revision"] = None

    elif change_type == "post_sound_prompt":
        gate = gates.get("final_compile")
        if not isinstance(gate, dict):
            gate = {}
            gates["final_compile"] = gate
        _reset_gate(gate)
        invalidated.append("final_compile")

    interaction = data.get("interaction_state")
    if isinstance(interaction, dict) and change_type != "diagnostic":
        if change_type in FULL_REAPPROVAL_CHANGES:
            interaction["current_stage"] = "S1"
        elif change_type in SHOT_REAPPROVAL_CHANGES:
            interaction["current_stage"] = "S3"
        else:
            interaction["current_stage"] = "S9"
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


def _validate_content_profile(
    data: dict[str, Any], errors: list[str], schema_version: str
) -> None:
    profile = data.get("content_profile")
    if not isinstance(profile, dict):
        errors.append(f"schema {schema_version} 缺少 content_profile")
        return

    if schema_version in {"1.5", "1.6"}:
        if profile.get("routing_policy") != "explicit_normal_adult_split":
            errors.append("content_profile.routing_policy 必须为 explicit_normal_adult_split")
        if profile.get("audio_policy") != "integrated_av":
            errors.append("content_profile.audio_policy 必须为 integrated_av")

    mode = profile.get("mode")
    if mode not in CONTENT_MODES:
        errors.append(f"content_profile.mode 无效: {mode}")
        return

    intimacy = profile.get("intimacy")
    if mode == "general":
        if intimacy is not None:
            errors.append("general 内容不得携带 intimacy 配置")
        return

    if not isinstance(intimacy, dict):
        errors.append("adult_intimacy 模式缺少 intimacy 配置")
        return

    if intimacy.get("content_level") not in INTIMACY_LEVELS:
        errors.append(f"成人亲密内容等级无效: {intimacy.get('content_level')}")
    if intimacy.get("consent_status") != "affirmative_and_reversible":
        errors.append("成人亲密内容必须记录明确、持续且可撤回的同意")
    if intimacy.get("youth_coding") is not False:
        errors.append("成人亲密内容不得包含未成年、年龄模糊或校园/幼态编码")
    if intimacy.get("escalation_policy") != "explicit_approval_required":
        errors.append("成人亲密内容提高尺度必须明确批准")

    participants = _require_list(intimacy.get("participants"), "content_profile.intimacy.participants", errors)
    if not participants:
        errors.append("成人亲密内容至少需要一个参与者")
    participant_ids: list[str] = []
    for index, participant in enumerate(participants):
        if not isinstance(participant, dict):
            errors.append(f"成人亲密参与者[{index}] 必须是对象")
            continue
        character_id = participant.get("character_id")
        if not isinstance(character_id, str) or not character_id:
            errors.append(f"成人亲密参与者[{index}] 缺少 character_id")
        else:
            participant_ids.append(character_id)
        if participant.get("adult_confirmed") is not True:
            errors.append(f"成人亲密参与者 {character_id} 未确认成年")
        age_years = participant.get("age_years")
        if not isinstance(age_years, int) or isinstance(age_years, bool) or age_years < 18:
            errors.append(f"成人亲密参与者 {character_id} age_years 必须为不低于18的整数")
        if participant.get("adult_coded_presentation") is not True:
            errors.append(f"成人亲密参与者 {character_id} 缺少明确成人化呈现")
        if participant.get("source_authorization") not in SOURCE_AUTHORIZATIONS:
            errors.append(f"成人亲密参与者 {character_id} 来源未获授权")
    if len(participant_ids) != len(set(participant_ids)):
        errors.append("成人亲密参与者 character_id 重复")

    for field in ("prohibited_elements", "camera_boundaries", "coverage_boundaries"):
        _require_list(intimacy.get(field), f"content_profile.intimacy.{field}", errors)
    locked_revision = intimacy.get("locked_revision")
    if locked_revision is not None and locked_revision != data.get("revision"):
        errors.append("content_profile.intimacy.locked_revision 与当前 revision 不一致")


def _validate_adult_model_profile(data: dict[str, Any], errors: list[str]) -> None:
    model = data.get("adult_model_profile")
    if not isinstance(model, dict):
        errors.append("schema 1.5+ 缺少 adult_model_profile")
        return
    if model.get("model") != "wan3.0-video":
        errors.append("adult_model_profile.model 必须为 wan3.0-video")
    if model.get("official_limits") != WAN_OFFICIAL_LIMITS:
        errors.append("adult_model_profile.official_limits 与 Wan 3.0 官方基线不一致")
    effective = model.get("effective_limits")
    if not isinstance(effective, dict):
        errors.append("缺少 adult_model_profile.effective_limits")
    else:
        for key, official_max in WAN_OFFICIAL_LIMITS.items():
            value = effective.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > official_max:
                errors.append(
                    f"adult_model_profile.effective_limits.{key} 必须为 1–{official_max} 的整数"
                )
    if not isinstance(model.get("verified_source"), str) or not model.get("verified_source"):
        errors.append("adult_model_profile 缺少 verified_source")


def _validate_prompt_limits(
    profile: Any,
    profile_name: str,
    target_model: str,
    errors: list[str],
) -> None:
    if not isinstance(profile, dict):
        return
    limits = profile.get("prompt_limits")
    if not isinstance(limits, dict):
        errors.append(f"{profile_name} 缺少 prompt_limits")
        return

    official_max = limits.get("official_max_characters")
    official_status = limits.get("official_status")
    effective_max = limits.get("effective_max_characters")
    soft_max = limits.get("production_soft_max_characters")

    if target_model == "seedance-2.5":
        if official_max is not None or official_status != "not_published":
            errors.append("Seedance 2.5 官方尚未公布提示词字符上限，不得伪造官方硬限制")
        if limits.get("counting_rule") != "verify_current_entry":
            errors.append("model_profile.prompt_limits.counting_rule 必须为 verify_current_entry")
    elif target_model == "wan3.0":
        if official_max != WAN_PROMPT_MAX_CHARACTERS or official_status != "published":
            errors.append("Wan 3.0 官方提示词上限必须记录为 20000 字符")
        if limits.get("counting_rule") != "one_chinese_character_or_letter_equals_one":
            errors.append(
                "adult_model_profile.prompt_limits.counting_rule 必须为 "
                "one_chinese_character_or_letter_equals_one"
            )

    if effective_max is not None:
        if not isinstance(effective_max, int) or isinstance(effective_max, bool) or effective_max < 1:
            errors.append(f"{profile_name}.prompt_limits.effective_max_characters 必须为正整数或 null")
        elif isinstance(official_max, int) and effective_max > official_max:
            errors.append(f"{profile_name}.prompt_limits.effective_max_characters 不得超过官方上限")
    if not isinstance(soft_max, int) or isinstance(soft_max, bool) or soft_max < 1:
        errors.append(f"{profile_name}.prompt_limits.production_soft_max_characters 必须为正整数")
    elif isinstance(effective_max, int) and soft_max > effective_max:
        errors.append(f"{profile_name}.prompt_limits.production_soft_max_characters 不得超过有效硬限制")
    if limits.get("overflow_policy") != "compress_then_split_never_truncate":
        errors.append(
            f"{profile_name}.prompt_limits.overflow_policy 必须为 compress_then_split_never_truncate"
        )
    if not isinstance(limits.get("verified_source"), str) or not limits.get("verified_source"):
        errors.append(f"{profile_name}.prompt_limits 缺少 verified_source")


def count_prompt_characters(text: str) -> int:
    """Count Unicode code points conservatively for prompt-limit preflight."""
    return len(text)


def _validate_compiled_prompts(
    data: dict[str, Any],
    segments: list[Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    prompts = _require_list(data.get("compiled_prompts"), "compiled_prompts", errors)
    segment_map = {
        segment.get("id"): segment
        for segment in segments
        if isinstance(segment, dict) and isinstance(segment.get("id"), str)
    }
    prompt_ids: list[str] = []
    prompt_segment_ids: list[str] = []
    profiles = {
        "seedance-2.5": data.get("model_profile", {}),
        "wan3.0": data.get("adult_model_profile", {}),
    }

    for index, prompt in enumerate(prompts):
        if not isinstance(prompt, dict):
            errors.append(f"compiled_prompts[{index}] 必须是对象")
            continue
        prompt_id = prompt.get("id")
        segment_id = prompt.get("segment_id")
        target_model = prompt.get("target_model")
        text = prompt.get("text")
        if not isinstance(prompt_id, str) or not prompt_id:
            errors.append(f"compiled_prompts[{index}] 缺少 id")
        else:
            prompt_ids.append(prompt_id)
        if not isinstance(segment_id, str) or not segment_id:
            errors.append(f"compiled_prompts[{index}] 缺少 segment_id")
            continue
        prompt_segment_ids.append(segment_id)
        segment = segment_map.get(segment_id)
        if segment is None:
            errors.append(f"最终提示词 {prompt_id} 引用了不存在的片段 {segment_id}")
        if target_model not in PROMPT_TARGET_MODELS:
            errors.append(f"最终提示词 {prompt_id} target_model 无效: {target_model}")
        elif segment is not None and target_model != segment.get("target_model"):
            errors.append(f"最终提示词 {prompt_id} 与片段 {segment_id} 的目标模型不一致")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"最终提示词 {prompt_id} 缺少 text")
            continue
        if MODULAR_PROMPT_START_RE.search(text):
            errors.append(f"最终提示词 {prompt_id} 必须从环境、人物或动作自然展开，不得以镜头字段或时长参数开头")
        actual_count = count_prompt_characters(text)
        if prompt.get("character_count") != actual_count:
            errors.append(f"最终提示词 {prompt_id} character_count 应为 {actual_count}")
        if prompt.get("compiled_revision") != data.get("revision"):
            errors.append(f"最终提示词 {prompt_id} compiled_revision 与当前 revision 不一致")

        profile = profiles.get(target_model, {})
        limits = profile.get("prompt_limits", {}) if isinstance(profile, dict) else {}
        hard_max = limits.get("effective_max_characters")
        soft_max = limits.get("production_soft_max_characters")
        if isinstance(hard_max, int) and actual_count > hard_max:
            errors.append(f"最终提示词 {prompt_id} 长度 {actual_count} 超过有效硬限制 {hard_max}")
        elif isinstance(soft_max, int) and actual_count > soft_max:
            warnings.append(f"最终提示词 {prompt_id} 长度 {actual_count} 超过制作软预算 {soft_max}")
        if target_model == "wan3.0" and prompt.get("prompt_extend") is True:
            warnings.append(f"最终提示词 {prompt_id} 启用 prompt_extend，可能改写已锁定 Canon，需复核扩写结果")

    if len(prompt_ids) != len(set(prompt_ids)):
        errors.append("compiled_prompts id 重复")
    if len(prompt_segment_ids) != len(set(prompt_segment_ids)):
        errors.append("同一片段绑定了多个最终提示词")
    final_status = data.get("approval_gates", {}).get("final_compile", {}).get("status")
    if final_status in COMPLETE_GATE_STATUSES and segments:
        missing = sorted(set(segment_map) - set(prompt_segment_ids))
        if missing:
            errors.append("final_compile 已完成但以下片段缺少最终提示词: " + ", ".join(missing))


def _validate_source_spans(
    data: dict[str, Any], errors: list[str]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    ledger = _require_list(data.get("source_span_ledger"), "source_span_ledger", errors)
    span_map: dict[str, dict[str, Any]] = {}
    source_orders: list[int] = []
    for index, span in enumerate(ledger):
        if not isinstance(span, dict):
            errors.append(f"source_span_ledger[{index}] 必须是对象")
            continue
        span_id = span.get("id")
        if not isinstance(span_id, str) or not span_id:
            errors.append(f"source_span_ledger[{index}] 缺少 id")
            continue
        if span_id in span_map:
            errors.append(f"原文跨度 id 重复: {span_id}")
        span_map[span_id] = span
        source_order = span.get("source_order")
        if not isinstance(source_order, int) or isinstance(source_order, bool) or source_order < 1:
            errors.append(f"原文跨度 {span_id} source_order 必须为正整数")
        else:
            source_orders.append(source_order)
        if not isinstance(span.get("source_locator"), str) or not span.get("source_locator").strip():
            errors.append(f"原文跨度 {span_id} 缺少 source_locator")
        if span.get("lane") not in CONTENT_LANES:
            errors.append(f"原文跨度 {span_id} lane 无效: {span.get('lane')}")
        if span.get("status") not in {"routed", "blocked"}:
            errors.append(f"原文跨度 {span_id} status 必须为 routed 或 blocked")
        if span.get("status") == "blocked" and not span.get("block_reason"):
            errors.append(f"被阻断原文跨度 {span_id} 缺少 block_reason")
    if len(source_orders) != len(set(source_orders)):
        errors.append("原文跨度 source_order 重复")

    segments = data.get("segments")
    segment_map = {
        segment.get("id"): segment
        for segment in segments
        if isinstance(segments, list) and isinstance(segment, dict) and segment.get("id")
    } if isinstance(segments, list) else {}
    for span_id, span in span_map.items():
        segment_id = span.get("segment_id")
        if span.get("status") == "routed" and segment_id not in segment_map:
            errors.append(f"原文跨度 {span_id} 已路由但 segment_id 不存在: {segment_id}")
        if segment_id in segment_map and span.get("lane") != segment_map[segment_id].get("content_lane"):
            errors.append(f"原文跨度 {span_id} lane 与片段 {segment_id} 不一致")
    return span_map, segment_map


def _require_nonempty_string(value: Any, field: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} 必须是非空字符串")
        return False
    return True


def _validate_visual_bible(data: dict[str, Any], errors: list[str]) -> None:
    bible = data.get("visual_bible")
    if not isinstance(bible, dict):
        errors.append("schema 1.6 缺少 visual_bible")
        return
    if bible.get("camera_policy") != "motivated_only":
        errors.append("visual_bible.camera_policy 必须为 motivated_only")
    if bible.get("axis_and_eyeline_policy") != "preserve_or_motivate_change":
        errors.append(
            "visual_bible.axis_and_eyeline_policy 必须为 preserve_or_motivate_change"
        )
    lighting = bible.get("lighting")
    if not isinstance(lighting, dict):
        errors.append("visual_bible 缺少 lighting")
        return
    for field in (
        "time_weather",
        "key_direction",
        "key_quality",
        "contrast_level",
        "fill_policy",
        "separation",
        "color_relationship",
        "exposure_priority",
    ):
        _require_nonempty_string(lighting.get(field), f"visual_bible.lighting.{field}", errors)
    for field in ("motivated_sources", "practicals"):
        _require_list(lighting.get(field), f"visual_bible.lighting.{field}", errors)
    locked_revision = lighting.get("locked_revision")
    if locked_revision is not None and locked_revision != data.get("revision"):
        errors.append("visual_bible.lighting.locked_revision 与当前 revision 不一致")


def _validate_performance_arc(segment: dict[str, Any], errors: list[str]) -> None:
    sid = segment.get("id", "<unknown>")
    arc = segment.get("performance_arc")
    if not isinstance(arc, dict):
        errors.append(f"片段 {sid} 缺少 performance_arc")
        return
    for field in ("goal", "trigger", "dominant_emotion", "residual_state"):
        _require_nonempty_string(arc.get(field), f"片段 {sid} performance_arc.{field}", errors)
    secondary = arc.get("secondary_leak")
    if secondary is not None and (not isinstance(secondary, str) or not secondary.strip()):
        errors.append(f"片段 {sid} performance_arc.secondary_leak 必须为非空字符串或 null")
    for field in ("intensity_start", "intensity_end"):
        if arc.get(field) not in PERFORMANCE_INTENSITIES:
            errors.append(f"片段 {sid} performance_arc.{field} 无效: {arc.get(field)}")
    tracks = _require_list(
        arc.get("active_tracks"), f"片段 {sid} performance_arc.active_tracks", errors
    )
    if not tracks:
        errors.append(f"片段 {sid} performance_arc 至少需要一条活跃表演轨")
    invalid = set(tracks) - PERFORMANCE_TRACKS if all(isinstance(x, str) for x in tracks) else set()
    if invalid:
        errors.append(f"片段 {sid} performance_arc 存在无效表演轨: {sorted(invalid)}")
    if len(tracks) != len(set(x for x in tracks if isinstance(x, str))):
        errors.append(f"片段 {sid} performance_arc.active_tracks 重复")


def _validate_camera_plan(segment: dict[str, Any], errors: list[str]) -> None:
    sid = segment.get("id", "<unknown>")
    plan = segment.get("camera_plan")
    if not isinstance(plan, dict):
        errors.append(f"片段 {sid} 缺少 camera_plan")
        return
    for field in (
        "watching_reason",
        "axis_side",
        "eyeline_map",
        "screen_direction",
        "framing_and_perspective",
        "camera_height_and_angle",
        "movement",
        "movement_motivation",
        "focus_path",
        "cut_reason",
        "end_composition",
    ):
        _require_nonempty_string(plan.get(field), f"片段 {sid} camera_plan.{field}", errors)


def _validate_lighting_state(segment: dict[str, Any], errors: list[str]) -> None:
    sid = segment.get("id", "<unknown>")
    state = segment.get("lighting_state")
    if not isinstance(state, dict):
        errors.append(f"片段 {sid} 缺少 lighting_state")
        return
    snapshots: dict[str, Any] = {}
    for edge in ("start", "end"):
        snapshot = state.get(edge)
        snapshots[edge] = snapshot
        if not isinstance(snapshot, dict):
            errors.append(f"片段 {sid} lighting_state.{edge} 必须是对象")
            continue
        _require_list(
            snapshot.get("motivated_sources"),
            f"片段 {sid} lighting_state.{edge}.motivated_sources",
            errors,
        )
        for field in ("key_direction", "color_relationship", "exposure_priority"):
            _require_nonempty_string(
                snapshot.get(field), f"片段 {sid} lighting_state.{edge}.{field}", errors
            )
    if isinstance(snapshots.get("start"), dict) and isinstance(snapshots.get("end"), dict):
        changed = snapshots["start"] != snapshots["end"]
        trigger = state.get("change_trigger")
        if changed and (not isinstance(trigger, str) or not trigger.strip()):
            errors.append(f"片段 {sid} 光向/综合色温/曝光发生变化但缺少 change_trigger")
        if not changed and trigger is not None and not isinstance(trigger, str):
            errors.append(f"片段 {sid} lighting_state.change_trigger 必须为字符串或 null")


def _validate_intimacy_beats(
    segment: dict[str, Any], span_map: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    sid = segment.get("id", "<unknown>")
    lane = segment.get("content_lane")
    beats = segment.get("intimacy_beats")
    if lane == "normal":
        if beats:
            errors.append(f"正常片段 {sid} 不得携带 intimacy_beats")
        return
    if not isinstance(beats, list) or not beats:
        errors.append(f"成人片段 {sid} 缺少 intimacy_beats")
        return

    segment_spans = set(segment.get("source_span_ids", []))
    expected_start = 0.0
    beat_ids: list[str] = []
    beat_span_ids: list[str] = []
    for index, beat in enumerate(beats):
        if not isinstance(beat, dict):
            errors.append(f"成人片段 {sid} intimacy_beats[{index}] 必须是对象")
            continue
        beat_id = beat.get("id")
        if not isinstance(beat_id, str) or not beat_id:
            errors.append(f"成人片段 {sid} intimacy_beats[{index}] 缺少 id")
        else:
            beat_ids.append(beat_id)
        span_id = beat.get("source_span_id")
        if span_id not in segment_spans or span_id not in span_map:
            errors.append(f"成人片段 {sid} 动作节拍 {beat_id} 引用了无效原文跨度 {span_id}")
        elif isinstance(span_id, str):
            beat_span_ids.append(span_id)
        start = beat.get("start")
        end = beat.get("end")
        if not isinstance(start, (int, float)) or isinstance(start, bool) or not isinstance(
            end, (int, float)
        ) or isinstance(end, bool):
            errors.append(f"成人片段 {sid} 动作节拍 {beat_id} 时间必须为数字")
        else:
            if abs(float(start) - expected_start) > 0.001:
                errors.append(
                    f"成人片段 {sid} 动作节拍 {beat_id} 起点不连续: {start}，期望 {expected_start}"
                )
            if end <= start:
                errors.append(f"成人片段 {sid} 动作节拍 {beat_id} 终点必须大于起点")
            expected_start = float(end)
        _require_nonempty_string(beat.get("initiator"), f"动作节拍 {beat_id}.initiator", errors)
        if beat.get("response") not in {"affirmative_and_reversible", "self_directed"}:
            errors.append(f"动作节拍 {beat_id}.response 必须明确且可撤回")
        if beat.get("action_family") not in INTIMACY_ACTION_FAMILIES:
            errors.append(f"动作节拍 {beat_id}.action_family 无效")
        for field in ("contact_map", "support_map"):
            values = _require_list(beat.get(field), f"动作节拍 {beat_id}.{field}", errors)
            if not values:
                errors.append(f"动作节拍 {beat_id}.{field} 不能为空")
        for field in (
            "movement_vector",
            "cadence",
            "coverage_before",
            "coverage_after",
            "consent_checkpoint",
            "sound",
            "camera_boundary",
            "end_state",
        ):
            _require_nonempty_string(beat.get(field), f"动作节拍 {beat_id}.{field}", errors)
    if len(beat_ids) != len(set(beat_ids)):
        errors.append(f"成人片段 {sid} intimacy_beats id 重复")
    if len(beat_span_ids) != len(set(beat_span_ids)):
        errors.append(f"成人片段 {sid} 的同一原文动作跨度被多个 intimacy_beats 重复使用")
    duration = segment.get("duration_seconds")
    if isinstance(duration, (int, float)) and not isinstance(duration, bool):
        if abs(expected_start - float(duration)) > 0.001:
            errors.append(
                f"成人片段 {sid} 动作节拍末点应为 {duration} 秒，实际为 {expected_start}"
            )


def _validate_transition_ledger(
    data: dict[str, Any],
    segments: list[Any],
    span_map: dict[str, dict[str, Any]],
    asset_ids: list[Any],
    errors: list[str],
) -> None:
    ledger = _require_list(data.get("transition_ledger"), "transition_ledger", errors)
    valid_segments = [segment for segment in segments if isinstance(segment, dict)]
    pair_map = {
        (valid_segments[index].get("id"), valid_segments[index + 1].get("id")): index
        for index in range(max(0, len(valid_segments) - 1))
    }
    transition_map: dict[str, dict[str, Any]] = {}
    pair_transition_ids: dict[tuple[Any, Any], str] = {}
    asset_map = {
        item.get("id"): item
        for item in data.get("assets", [])
        if isinstance(item, dict) and item.get("id")
    }
    used_pairs: list[tuple[Any, Any]] = []
    for index, entry in enumerate(ledger):
        if not isinstance(entry, dict):
            errors.append(f"transition_ledger[{index}] 必须是对象")
            continue
        transition_id = entry.get("id")
        if not isinstance(transition_id, str) or not transition_id:
            errors.append(f"transition_ledger[{index}] 缺少 id")
            continue
        if transition_id in transition_map:
            errors.append(f"转场 id 重复: {transition_id}")
        transition_map[transition_id] = entry
        pair = (entry.get("from_segment_id"), entry.get("to_segment_id"))
        used_pairs.append(pair)
        if pair not in pair_transition_ids:
            pair_transition_ids[pair] = transition_id
        if pair not in pair_map:
            errors.append(f"转场 {transition_id} 必须连接相邻片段，实际为 {pair[0]} -> {pair[1]}")
            continue
        from_segment = valid_segments[pair_map[pair]]
        to_segment = valid_segments[pair_map[pair] + 1]
        expected_lane_change = (
            "same_lane"
            if from_segment.get("content_lane") == to_segment.get("content_lane")
            else f"{from_segment.get('content_lane')}_to_{to_segment.get('content_lane')}"
        )
        if entry.get("lane_change") != expected_lane_change:
            errors.append(
                f"转场 {transition_id} lane_change 应为 {expected_lane_change}，实际为 {entry.get('lane_change')}"
            )
        if entry.get("lane_change") not in LANE_CHANGES:
            errors.append(f"转场 {transition_id} lane_change 无效")
        bridge_types = _require_list(
            entry.get("bridge_types"), f"转场 {transition_id}.bridge_types", errors
        )
        if not bridge_types:
            errors.append(f"转场 {transition_id} 至少需要一种 bridge_type")
        invalid_bridges = set(bridge_types) - BRIDGE_TYPES if all(
            isinstance(item, str) for item in bridge_types
        ) else set()
        if invalid_bridges:
            errors.append(f"转场 {transition_id} bridge_types 无效: {sorted(invalid_bridges)}")
        source_span_ids = _require_list(
            entry.get("source_span_ids"), f"转场 {transition_id}.source_span_ids", errors
        )
        if not source_span_ids:
            errors.append(f"转场 {transition_id} 至少需要一个 source_span_id")
        allowed_spans = set(from_segment.get("source_span_ids", [])) | set(
            to_segment.get("source_span_ids", [])
        )
        for span_id in source_span_ids:
            if span_id not in span_map or span_id not in allowed_spans:
                errors.append(f"转场 {transition_id} 引用了无效原文跨度 {span_id}")
        for field in (
            "visual_anchor",
            "action_carry",
            "performance_residue",
            "lighting_carry",
            "audio_carry",
            "wardrobe_and_coverage",
            "consent_state",
        ):
            _require_nonempty_string(entry.get(field), f"转场 {transition_id}.{field}", errors)
        if entry.get("handoff_mode") not in HANDOFF_MODES:
            errors.append(f"转场 {transition_id}.handoff_mode 无效")
        asset_id = entry.get("shared_boundary_asset_id")
        if entry.get("handoff_mode") == "shared_boundary_keyframe":
            if not isinstance(asset_id, str) or not asset_id:
                errors.append(f"转场 {transition_id} 共享边界关键帧缺少资产 ID")
            elif asset_id not in asset_ids:
                errors.append(f"转场 {transition_id} 引用了不存在的共享边界资产 {asset_id}")
            elif entry.get("status") == "approved" and asset_map.get(asset_id, {}).get("status") != "approved":
                errors.append(f"已批准转场 {transition_id} 的共享边界资产尚未 approved")
        elif asset_id is not None:
            errors.append(f"转场 {transition_id} 使用 state_only 时 shared_boundary_asset_id 必须为 null")
        boundary = entry.get("boundary_action")
        if not isinstance(boundary, dict):
            errors.append(f"转场 {transition_id} 缺少 boundary_action")
        else:
            _require_nonempty_string(
                boundary.get("outgoing_event"),
                f"转场 {transition_id}.boundary_action.outgoing_event",
                errors,
            )
            _require_nonempty_string(
                boundary.get("incoming_event"),
                f"转场 {transition_id}.boundary_action.incoming_event",
                errors,
            )
            if boundary.get("handoff_rule") != "non_overlapping_sequential":
                errors.append(
                    f"转场 {transition_id}.boundary_action.handoff_rule 必须为 non_overlapping_sequential"
                )
            outgoing_event = boundary.get("outgoing_event")
            incoming_event = boundary.get("incoming_event")
            if (
                isinstance(outgoing_event, str)
                and isinstance(incoming_event, str)
                and outgoing_event.strip() == incoming_event.strip()
            ):
                errors.append(f"转场 {transition_id} 的边界动作重复，必须拆成前后不重叠事件")

        from_light = from_segment.get("lighting_state", {}).get("end")
        to_light = to_segment.get("lighting_state", {}).get("start")
        lighting_change_trigger = entry.get("lighting_change_trigger")
        if isinstance(from_light, dict) and isinstance(to_light, dict) and from_light != to_light:
            if not isinstance(lighting_change_trigger, str) or not lighting_change_trigger.strip():
                errors.append(f"转场 {transition_id} 出现光向/综合色温/曝光突变但缺少 lighting_change_trigger")
        elif lighting_change_trigger is not None and not isinstance(lighting_change_trigger, str):
            errors.append(f"转场 {transition_id}.lighting_change_trigger 必须为字符串或 null")
        if entry.get("status") not in {"planned", "approved"}:
            errors.append(f"转场 {transition_id}.status 必须为 planned 或 approved")

    if len(used_pairs) != len(set(used_pairs)):
        errors.append("同一相邻片段对存在重复转场")
    for pair in pair_map:
        if used_pairs.count(pair) != 1:
            errors.append(f"相邻片段 {pair[0]} -> {pair[1]} 必须且只能有一个转场")
    for index, segment in enumerate(valid_segments):
        incoming = segment.get("incoming_transition_id")
        outgoing = segment.get("outgoing_transition_id")
        expected_incoming = (
            None
            if index == 0
            else pair_transition_ids.get((valid_segments[index - 1].get("id"), segment.get("id")))
        )
        expected_outgoing = (
            None
            if index == len(valid_segments) - 1
            else pair_transition_ids.get((segment.get("id"), valid_segments[index + 1].get("id")))
        )
        if incoming != expected_incoming:
            errors.append(f"片段 {segment.get('id')} incoming_transition_id 与相邻片段不一致")
        if outgoing != expected_outgoing:
            errors.append(f"片段 {segment.get('id')} outgoing_transition_id 与相邻片段不一致")
        if incoming is not None and incoming not in transition_map:
            errors.append(f"片段 {segment.get('id')} 引用了不存在的 incoming_transition_id {incoming}")
        if outgoing is not None and outgoing not in transition_map:
            errors.append(f"片段 {segment.get('id')} 引用了不存在的 outgoing_transition_id {outgoing}")
    for pair, pair_index in pair_map.items():
        expected_id = valid_segments[pair_index].get("outgoing_transition_id")
        if expected_id is not None:
            entry = transition_map.get(expected_id)
            if entry and (entry.get("from_segment_id"), entry.get("to_segment_id")) != pair:
                errors.append(f"转场 {expected_id} 的端点与片段引用不一致")


def _validate_v12plus(
    data: dict[str, Any], errors: list[str], warnings: list[str], schema_version: str
) -> None:
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
    if hook is not None and (
        not isinstance(hook, list)
        or len(hook) != 2
        or not all(isinstance(item, (int, float)) for item in hook)
        or hook[0] < 0
        or hook[1] <= hook[0]
    ):
        errors.append("rhythm_profile.hook_window_seconds 必须为 null 或递增的两个非负数字")
    if schema_version == "1.2" and hook is None:
        errors.append("schema 1.2 的 rhythm_profile.hook_window_seconds 不能为空")
    interval = rhythm.get("progression_interval_seconds")
    if interval is not None and (not isinstance(interval, int) or interval < 1):
        errors.append("rhythm_profile.progression_interval_seconds 必须为 null 或正整数")
    if schema_version == "1.2" and interval is None:
        errors.append("schema 1.2 的 rhythm_profile.progression_interval_seconds 不能为空")
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

        if task_type == "performance_design":
            scope = task.get("performance_scope")
            if not isinstance(scope, dict):
                errors.append(f"表演任务 {task_id} 缺少 performance_scope")
                scope = {}
            source_span_ids = _require_list(
                scope.get("source_span_ids"),
                f"表演任务 {task_id} performance_scope.source_span_ids",
                errors,
            )
            character_ids = _require_list(
                scope.get("character_ids"),
                f"表演任务 {task_id} performance_scope.character_ids",
                errors,
            )
            proposed_arcs = _require_list(
                task.get("proposed_performance_arcs"),
                f"表演任务 {task_id} proposed_performance_arcs",
                errors,
            )
            if not source_span_ids:
                errors.append(f"表演任务 {task_id} 至少需要一个 source_span_id")
            if not character_ids:
                errors.append(f"表演任务 {task_id} 至少需要一个 character_id")
            if task.get("status") in {"approved", "completed"} and not proposed_arcs:
                errors.append(f"表演任务 {task_id} 已完成但缺少 proposed_performance_arcs")
            for arc_index, arc in enumerate(proposed_arcs):
                if not isinstance(arc, dict):
                    errors.append(f"表演任务 {task_id} arc[{arc_index}] 必须是对象")
                    continue
                for field in ("target_id", "trigger", "residual_state"):
                    if not isinstance(arc.get(field), str) or not arc.get(field).strip():
                        errors.append(f"表演任务 {task_id} arc[{arc_index}] 缺少 {field}")
                tracks = _require_list(
                    arc.get("active_tracks"),
                    f"表演任务 {task_id} arc[{arc_index}].active_tracks",
                    errors,
                )
                invalid_tracks = set(tracks) - PERFORMANCE_TRACKS
                if invalid_tracks:
                    errors.append(
                        f"表演任务 {task_id} arc[{arc_index}] 存在无效表演轨: "
                        f"{sorted(invalid_tracks)}"
                    )

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

    misplaced_fields = sorted(COLLABORATION_ONLY_FIELDS.intersection(data))
    if misplaced_fields:
        errors.append(
            "影视项目状态不得包含外部协作表字段: " + ", ".join(misplaced_fields)
        )

    schema_version = data.get("schema_version")
    if schema_version not in {"1.1", "1.2", "1.3", "1.4", "1.5", "1.6"}:
        errors.append("schema_version 必须为 1.1、1.2、1.3、1.4、1.5 或 1.6")
    elif schema_version == "1.1":
        warnings.append("schema_version 1.1 为兼容格式；建议升级到 1.6")
    else:
        _validate_v12plus(data, errors, warnings, schema_version)
        if schema_version in {"1.2", "1.3", "1.4", "1.5"}:
            warnings.append(f"schema_version {schema_version} 为兼容格式；建议升级到 1.6")
        if schema_version in {"1.4", "1.5", "1.6"}:
            _validate_content_profile(data, errors, schema_version)
        if schema_version in {"1.5", "1.6"}:
            _validate_adult_model_profile(data, errors)
        if schema_version == "1.6":
            _validate_visual_bible(data, errors)
            _validate_prompt_limits(data.get("model_profile"), "model_profile", "seedance-2.5", errors)
            _validate_prompt_limits(
                data.get("adult_model_profile"),
                "adult_model_profile",
                "wan3.0",
                errors,
            )

    if not data.get("project_id"):
        errors.append("缺少 project_id")
    if not isinstance(data.get("revision"), int) or data.get("revision", 0) < 1:
        errors.append("revision 必须是正整数")

    production_rules = data.get("production_rules")
    if not isinstance(production_rules, dict):
        errors.append("缺少 production_rules")
        production_rules = {}
    if schema_version in {"1.1", "1.2"}:
        if production_rules.get("drama_segment_seconds") != 30:
            errors.append("兼容状态的文戏单元必须为30秒")
        if production_rules.get("action_segment_seconds") != 25:
            errors.append("兼容状态的武戏单元必须为25秒")
    elif schema_version in {"1.3", "1.4"}:
        if production_rules.get("duration_policy") != "story_beat_first":
            errors.append("production_rules.duration_policy 必须为 story_beat_first")
        if production_rules.get("max_segment_seconds_from_model_profile") is not True:
            errors.append("production_rules.max_segment_seconds_from_model_profile 必须为 true")
        if production_rules.get("shot_count_policy") != "minimum_sufficient":
            errors.append("production_rules.shot_count_policy 必须为 minimum_sufficient")
        if production_rules.get("storyboard_layout") != "adaptive":
            errors.append("production_rules.storyboard_layout 必须为 adaptive")
    else:
        if production_rules.get("duration_policy") != "story_beat_first":
            errors.append("production_rules.duration_policy 必须为 story_beat_first")
        if production_rules.get("max_segment_seconds_from_model_profile") is not True:
            errors.append("production_rules.max_segment_seconds_from_model_profile 必须为 true")
        if production_rules.get("shot_count_policy") != "minimum_sufficient":
            errors.append("production_rules.shot_count_policy 必须为 minimum_sufficient")
        if production_rules.get("storyboard_layout") != "normal_lane_4x4_16_panel":
            errors.append("schema 1.5+ 正常段故事板必须为 4x4 十六宫格")
        if production_rules.get("adult_storyboard_layout") != "not_required":
            errors.append("schema 1.5 成人段不得生成十六宫格")
        if production_rules.get("adult_segment_target_seconds") != 30:
            errors.append("成人段单次最大目标容器必须为 30 秒")
        if production_rules.get("adult_final_segment_policy") != "actual_duration_no_padding":
            errors.append("成人末段必须使用实际时长且不得注水")
        if production_rules.get("audio_generation") != "integrated_av":
            errors.append("完整生产默认必须使用音画一体生成")
        if schema_version == "1.6":
            expected_rules = {
                "camera_movement_policy": "motivated_only",
                "lighting_continuity_policy": "change_requires_motivation",
                "lane_transition_policy": "explicit_state_handoff",
                "performance_timing_policy": "event_driven",
                "prompt_prose_policy": "camera_embedded_natural_prose",
                "adult_description_policy": "maximum_non_graphic_detail_no_silent_omission",
                "prompt_length_policy": "official_hard_limit_plus_adaptive_soft_budget",
            }
            for field, expected in expected_rules.items():
                if production_rules.get(field) != expected:
                    errors.append(f"production_rules.{field} 必须为 {expected}")
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

    if schema_version in {"1.2", "1.3", "1.4", "1.5", "1.6"}:
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
    if schema_version in {"1.2", "1.3", "1.4", "1.5", "1.6"}:
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

    span_map: dict[str, dict[str, Any]] = {}
    if schema_version in {"1.5", "1.6"}:
        span_map, _ = _validate_source_spans(data, errors)

    project_pacing = data.get("rhythm_profile", {}).get("pacing")
    previous_end_state = None
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        sid = segment.get("id", "<unknown>")
        mode = segment.get("mode")
        duration = segment.get("duration_seconds")
        shots = segment.get("shots", [])

        content_lane = segment.get("content_lane") if schema_version in {"1.5", "1.6"} else "normal"
        target_model = segment.get("target_model") if schema_version in {"1.5", "1.6"} else "seedance-2.5"
        if schema_version in {"1.5", "1.6"}:
            if content_lane not in CONTENT_LANES:
                errors.append(f"片段 {sid} content_lane 无效: {content_lane}")
            elif target_model != LANE_TARGET_MODELS[content_lane]:
                errors.append(
                    f"片段 {sid} 的 {content_lane} 路必须指向 {LANE_TARGET_MODELS[content_lane]}"
                )
            if content_lane == "adult" and data.get("content_profile", {}).get("mode") != "adult_intimacy":
                errors.append(f"成人片段 {sid} 缺少 adult_intimacy 内容档案")
            source_span_ids = _require_list(
                segment.get("source_span_ids"), f"片段 {sid} source_span_ids", errors
            )
            if not source_span_ids:
                errors.append(f"片段 {sid} 至少需要一个 source_span_id")
            for span_id in source_span_ids:
                span = span_map.get(span_id)
                if span is None:
                    errors.append(f"片段 {sid} 引用了不存在的原文跨度 {span_id}")
                elif span.get("lane") != content_lane:
                    errors.append(f"片段 {sid} 与原文跨度 {span_id} 的 lane 不一致")

        if schema_version == "1.6":
            for transition_field in ("incoming_transition_id", "outgoing_transition_id"):
                if transition_field not in segment:
                    errors.append(f"片段 {sid} 缺少 {transition_field}")
            _validate_performance_arc(segment, errors)
            _validate_camera_plan(segment, errors)
            _validate_lighting_state(segment, errors)
            _validate_intimacy_beats(segment, span_map, errors)
            if content_lane == "adult" and segment.get("storyboard_asset_ids"):
                errors.append(f"成人片段 {sid} 不得绑定十六宫格 storyboard_asset_ids")

        if mode not in {"drama", "action"}:
            errors.append(f"片段 {sid} 的 mode 必须为 drama 或 action")
            continue
        if schema_version in {"1.1", "1.2"}:
            expected_duration = 30 if mode == "drama" else 25
            if duration != expected_duration:
                errors.append(f"兼容片段 {sid} 时长应为 {expected_duration} 秒，实际为 {duration}")
        else:
            expected_duration = duration
            if schema_version in {"1.5", "1.6"} and content_lane == "adult":
                effective_duration = data.get("adult_model_profile", {}).get(
                    "effective_limits", WAN_OFFICIAL_LIMITS
                ).get("duration_seconds", 30)
            else:
                effective_duration = effective_limits.get("duration_seconds", 30)
            if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
                errors.append(f"片段 {sid} duration_seconds 必须为正数")
                expected_duration = None
            elif not isinstance(effective_duration, int) or duration > effective_duration:
                errors.append(f"片段 {sid} 时长 {duration} 秒超过有效上限 {effective_duration}")
            for field in ("dramatic_unit", "duration_rationale", "shot_count_rationale"):
                if not isinstance(segment.get(field), str) or not segment.get(field).strip():
                    errors.append(f"片段 {sid} 缺少 {field}")
        if not isinstance(shots, list):
            errors.append(f"片段 {sid} shots 必须是数组")
            shots = []

        if schema_version in {"1.2", "1.3", "1.4", "1.5", "1.6"}:
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

        if shots and isinstance(expected_duration, (int, float)) and abs(expected_start - expected_duration) > 0.001:
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

    if schema_version == "1.6":
        _validate_transition_ledger(data, segments, span_map, asset_ids, errors)
        _validate_compiled_prompts(data, segments, errors, warnings)

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
