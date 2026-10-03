#!/usr/bin/env python3
"""Standard-library tests for project-state invariants and transitions."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_project_state import (
    GATE_ORDER,
    apply_change,
    approve_pending_gate,
    count_prompt_characters,
    validate,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_ROOT / "scripts" / "fixtures" / "project-state-1.9.json"


def template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def legacy_state(version: str) -> dict:
    state = template()
    state["schema_version"] = version
    state["stage"] = "S0"
    state["interaction_state"]["current_stage"] = "S0"
    state["production_rules"].update(
        {"drama_segment_seconds": 30, "action_segment_seconds": 25}
    )
    state["rhythm_profile"].update(
        {"hook_window_seconds": [0, 5], "progression_interval_seconds": 15}
    )
    if version in {"1.3", "1.4", "1.5", "1.6"}:
        state["production_rules"]["duration_policy"] = "story_beat_first"
    if version in {"1.3", "1.4"}:
        state["production_rules"]["storyboard_layout"] = "adaptive"
    return state


def adult_intimacy_state() -> dict:
    state = template()
    state["content_profile"] = {
        "mode": "adult_intimacy",
        "routing_policy": "explicit_normal_adult_split",
        "audio_policy": "integrated_av",
        "intimacy": {
            "content_level": "explicit_adult",
            "consent_status": "affirmative_and_reversible",
            "youth_coding": False,
            "escalation_policy": "explicit_approval_required",
            "participants": [
                {
                    "character_id": "CHAR-A01",
                    "age_years": 20,
                    "adult_confirmed": True,
                    "adult_coded_presentation": True,
                    "source_authorization": "fictional",
                }
            ],
            "prohibited_elements": ["coercion", "incapacitation"],
            "camera_boundaries": ["no_voyeuristic_hidden_camera"],
            "coverage_boundaries": [],
            "locked_revision": 1,
        },
    }
    return state


def enrich_segment(segment: dict, lane: str = "normal") -> dict:
    segment["content_lane"] = lane
    segment["target_model"] = "seedance-2.5" if lane == "normal" else "wan3.0"
    segment.setdefault(
        "performance_arc",
        {
            "goal": "完成当前戏剧动作",
            "trigger": "上一动作产生可见结果",
            "dominant_emotion": "克制",
            "secondary_leak": "短暂迟疑",
            "intensity_start": "restrained",
            "intensity_end": "clear",
            "active_tracks": ["gaze", "body_weight", "breathing_sound"],
            "residual_state": "呼吸尚未完全平复",
        },
    )
    segment.setdefault(
        "narrative_paragraph",
        {
            "meaning": "人物的选择改变了当前关系",
            "development": "人物观察结果后作出行动，对方以可见反应回应",
            "completion_cue": "双方都看见选择造成的关系结果",
            "forward_impulse": "人物准备执行下一项尚未开始的行动",
        },
    )
    segment.setdefault(
        "reentry_plan",
        {
            "anchor": "人物继承的动作结果",
            "opening_action": "人物从稳定状态开始新的选择",
            "inherited_state": "人物身份、位置、服装、道具、光线、呼吸和关系结果不变",
            "first_new_information": "观众先看见人物正在采取不同策略",
        },
    )
    segment.setdefault(
        "composition_plan",
        {
            "dominant_point": "画面右侧人物抬起的眼睛",
            "attention_path": "注意力从左侧窗框沿人物视线移向右侧人物抬起的眼睛",
            "depth_and_balance": "失焦门框为前景，两人在中景，窗户为背景；右侧亮面与左侧较大暗面平衡",
            "point_contrast": "眼睛由窗边高光提亮，背景保持低对比",
            "guiding_lines": [
                {
                    "source": "左侧窗框",
                    "direction": "向右下",
                    "destination": "人物视线落点",
                    "purpose": "把注意力带到关系变化",
                }
            ],
            "planes": {
                "foreground": "失焦门框轻遮挡左侧",
                "midground": "两名人物与动作关系",
                "background": "窗户和固定空间地标",
            },
            "negative_space": "人物视线前方保留约四分之一空间",
            "visual_weight": "右侧人物较亮，左侧人物以较大暗面平衡",
            "start_frame": "门框内先看见两人维持原距离",
            "end_frame": "回应后两人间距缩短且视线相接",
        },
    )
    segment.setdefault(
        "camera_plan",
        {
            "entry_view": "从人物继承的动作结果重新找到双方关系",
            "attention_progression": "注意力从人物选择转向对方回应，再回到关系结果",
            "viewpoint_turns": [
                {
                    "response_type": "pull-back",
                    "trigger": "对方作出改变关系的回应",
                    "camera_response": "观看位置让出两人的新距离",
                    "revealed_meaning": "选择已经改变双方关系",
                }
            ],
            "closing_view": "双方停在已经改变的关系状态上",
            "continuity": {
                "axis_side": "left",
                "eyeline_target": "对方双眼",
                "screen_direction": "left-to-right",
                "motion_in": "static",
                "motion_out": "static",
            },
        },
    )
    lighting_snapshot = {
        "motivated_sources": ["窗外日光"],
        "key_direction": "画面左侧",
        "color_relationship": "中性日光与室内微暖实景灯",
        "exposure_priority": "人物眼神与主要动作",
    }
    segment.setdefault(
        "lighting_state",
        {"start": copy.deepcopy(lighting_snapshot), "end": lighting_snapshot, "change_trigger": None},
    )
    segment.setdefault("incoming_transition_id", None)
    segment.setdefault("outgoing_transition_id", None)
    return segment


def intimacy_beat(span_id: str, duration: float) -> dict:
    return {
        "id": "IB-001",
        "source_span_id": span_id,
        "start": 0,
        "end": duration,
        "initiator": "CHAR-A01",
        "response": "affirmative_and_reversible",
        "action_family": "kissing_caressing",
        "contact_map": ["双方已批准的接触范围"],
        "support_map": ["双脚稳定着地并由床沿承重"],
        "movement_vector": "相向靠近后保持稳定",
        "cadence": "由试探转为连贯",
        "coverage_before": "按已批准边界保持覆盖",
        "coverage_after": "覆盖状态不变",
        "consent_checkpoint": "对方主动回应且可随时停止",
        "sound": "同步呼吸、衣料与环境声",
        "camera_boundary": "不越过已批准呈现范围",
        "end_state": "双方暂停并保持可继续确认的距离",
    }


def attach_segment(state: dict, segment: dict, lane: str = "normal") -> None:
    span_id = f"SPAN-{segment['id']}"
    enrich_segment(segment, lane)
    segment["source_span_ids"] = [span_id]
    if lane == "adult":
        segment.setdefault("intimacy_beats", [intimacy_beat(span_id, segment["duration_seconds"])])
    state["segments"] = [segment]
    state["source_span_ledger"] = [
        {
            "id": span_id,
            "source_order": 1,
            "source_locator": "测试原文第1段",
            "lane": lane,
            "status": "routed",
            "segment_id": segment["id"],
        }
    ]


def sequence_state(lanes: list[str], durations: list[float] | None = None) -> dict:
    state = adult_intimacy_state() if "adult" in lanes else template()
    state["approval_gates"]["script_adaptation"]["status"] = "not_required"
    durations = durations or [12 for _ in lanes]
    segments = []
    spans = []
    for index, (lane, duration) in enumerate(zip(lanes, durations), start=1):
        segment_id = f"SEG-{index:02d}"
        span_id = f"SPAN-{index:02d}"
        segment = enrich_segment(
            {
                "id": segment_id,
                "mode": "drama",
                "source_span_ids": [span_id],
                "duration_seconds": duration,
                "dramatic_unit": f"片段{index}完成一次关系变化",
                "duration_rationale": "按可见动作、回应、对白和声音试演估算",
                "shot_count_rationale": "单镜能完整承载当前观看理由",
                "rhythm_pacing": state["rhythm_profile"]["pacing"],
                "action_types": [],
                "shots": [{"number": 1, "start": 0, "end": duration, "asset_ids": []}],
                "start_state": f"STATE-{index - 1}",
                "end_state": f"STATE-{index}",
            },
            lane,
        )
        if lane == "adult":
            segment["intimacy_beats"] = [intimacy_beat(span_id, duration)]
        segments.append(segment)
        spans.append(
            {
                "id": span_id,
                "source_order": index,
                "source_locator": f"测试原文第{index}段",
                "lane": lane,
                "status": "routed",
                "segment_id": segment_id,
            }
        )
    transitions = []
    for index in range(len(segments) - 1):
        from_segment = segments[index]
        to_segment = segments[index + 1]
        transition_id = f"TR-{index + 1:02d}"
        from_segment["outgoing_transition_id"] = transition_id
        to_segment["incoming_transition_id"] = transition_id
        lane_change = (
            "same_lane"
            if from_segment["content_lane"] == to_segment["content_lane"]
            else f"{from_segment['content_lane']}_to_{to_segment['content_lane']}"
        )
        transitions.append(
            {
                "id": transition_id,
                "from_segment_id": from_segment["id"],
                "to_segment_id": to_segment["id"],
                "source_span_ids": [
                    from_segment["source_span_ids"][0],
                    to_segment["source_span_ids"][0],
                ],
                "lane_change": lane_change,
                "completed_meaning": from_segment["narrative_paragraph"]["meaning"],
                "forward_impulse": from_segment["narrative_paragraph"]["forward_impulse"],
                "reentry_anchor": to_segment["reentry_plan"]["anchor"],
                "inherited_state": to_segment["reentry_plan"]["inherited_state"],
                "edit_bridge": {
                    "match_basis": ["gaze"],
                    "bridge": "gaze-match",
                    "reason": "把上一段未执行的意图交给下一段的新选择",
                    "intentional_break": False,
                },
                "assembly_contract": {
                    "join_mode": "straight-cut",
                    "visual_join": "上一段人物停下的视线成为下一段新选择的起点",
                    "sound_join": "两段使用同一房间环境底声并在动作落点处直接切接",
                    "combined_meaning": "上一段未执行的意图在下一段转化为人物的新选择",
                },
                "lighting_change_trigger": None,
                "shared_boundary_asset_id": None,
                "handoff_mode": "state_only",
                "boundary_action": {
                    "outgoing_event": f"片段{index + 1}完成其末动作",
                    "incoming_event": to_segment["reentry_plan"]["opening_action"],
                    "handoff_rule": "non_overlapping_sequential",
                },
                "status": "planned",
            }
        )
    state["segments"] = segments
    state["source_span_ledger"] = spans
    state["transition_ledger"] = transitions
    return state


def specialist_task(task_type: str = "script_review") -> dict:
    task = {
        "id": "SP-001",
        "type": task_type,
        "status": "completed",
        "source_revision": 1,
        "target_ids": ["SCENE-01"],
        "diagnostic_only": True,
        "findings": [
            {
                "priority": "high",
                "evidence": "SCENE-01 中角色连续解释双方都知道的旧事",
                "impact": "冲突停滞且占用自然对白时长",
                "recommendation": "删除重复解释，改由当下选择暴露信息",
            }
        ],
    }
    if task_type == "dialogue_polish":
        task["natural_speech_risk"] = "high"
    if task_type == "performance_design":
        task.update(
            {
                "performance_scope": {
                    "source_span_ids": ["SPAN-N01"],
                    "character_ids": ["CHAR-A01", "CHAR-A02"],
                },
                "proposed_performance_arcs": [
                    {
                        "target_id": "SEG-01",
                        "trigger": "一人说出关键事实，另一人先移开视线再重新看回去",
                        "active_tracks": ["gaze", "breathing_sound"],
                        "residual_state": "回应后的迟疑继续留在呼吸里",
                    }
                ],
            }
        )
    if task_type == "post_sound":
        task.update(
            {
                "mode": "cue_sheet",
                "output_layer": "post_production",
                "writes_to_seedance_prompt": False,
                "cue_sheet": [
                    {
                        "timecode": "00:00-00:08",
                        "story_function": "克制铺底",
                        "entry_exit": "00:02 淡入，00:08 淡出",
                        "dialogue_ducking": "对白出现时降低音乐存在感",
                        "silence": "00:07 留半秒静默",
                        "licensing_note": "商用前保存授权记录",
                    }
                ],
            }
        )
    return task


class ProjectStateTests(unittest.TestCase):
    def test_v19_template_passes(self) -> None:
        errors, warnings = validate(template())
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_v19_rejects_invented_seedance_and_wrong_wan_prompt_limits(self) -> None:
        state = template()
        state["model_profile"]["prompt_limits"]["official_max_characters"] = 2000
        state["model_profile"]["prompt_limits"]["official_status"] = "published"
        state["adult_model_profile"]["prompt_limits"]["official_max_characters"] = 19999
        errors, _ = validate(state)
        self.assertTrue(any("Seedance 2.5 官方尚未公布" in item for item in errors))
        self.assertTrue(any("Wan 3.0 官方提示词上限" in item for item in errors))

    def test_compiled_prompt_count_and_model_are_validated(self) -> None:
        state = sequence_state(["normal"])
        text = "雨后的门廊里，她收起伞走向窗边，画面随着脚步缓缓靠近。"
        state["compiled_prompts"] = [
            {
                "id": "PROMPT-01",
                "segment_id": "SEG-01",
                "target_model": "wan3.0",
                "text": text,
                "character_count": count_prompt_characters(text) - 1,
                "compiled_revision": 1,
            }
        ]
        errors, _ = validate(state)
        self.assertTrue(any("character_count 应为" in item for item in errors))
        self.assertTrue(any("目标模型不一致" in item for item in errors))

    def test_compiled_prompt_rejects_modular_camera_opening(self) -> None:
        state = sequence_state(["normal"])
        text = "镜头：中景推进。她从门口走向窗边。"
        state["compiled_prompts"] = [
            {
                "id": "PROMPT-01",
                "segment_id": "SEG-01",
                "target_model": "seedance-2.5",
                "text": text,
                "character_count": count_prompt_characters(text),
                "compiled_revision": 1,
            }
        ]
        errors, _ = validate(state)
        self.assertTrue(any("不得以镜头字段或时长参数开头" in item for item in errors))

    def test_prompt_hard_limit_errors_and_soft_budget_warns(self) -> None:
        state = sequence_state(["normal"])
        text = "自然语言提示词超过预算"
        state["compiled_prompts"] = [
            {
                "id": "PROMPT-01",
                "segment_id": "SEG-01",
                "target_model": "seedance-2.5",
                "text": text,
                "character_count": count_prompt_characters(text),
                "compiled_revision": 1,
            }
        ]
        state["model_profile"]["prompt_limits"]["production_soft_max_characters"] = 5
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertTrue(any("超过制作软预算" in item for item in warnings))

        state["model_profile"]["prompt_limits"]["effective_max_characters"] = 5
        errors, _ = validate(state)
        self.assertTrue(any("超过有效硬限制" in item for item in errors))

    def test_final_compile_requires_one_prompt_per_segment(self) -> None:
        state = sequence_state(["normal"])
        for gate in state["approval_gates"].values():
            gate["status"] = "not_required"
            gate["approved_revision"] = None
        errors, _ = validate(state)
        self.assertTrue(any("缺少最终提示词" in item for item in errors))

    def test_wan_prompt_extend_requires_canon_review(self) -> None:
        state = sequence_state(["adult"])
        text = "卧室里，两位已确认自愿的成年人保持相互回应，动作与呼吸自然同步。"
        state["compiled_prompts"] = [
            {
                "id": "PROMPT-ADULT-01",
                "segment_id": "SEG-01",
                "target_model": "wan3.0",
                "text": text,
                "character_count": count_prompt_characters(text),
                "compiled_revision": 1,
                "prompt_extend": True,
            }
        ]
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertTrue(any("可能改写已锁定 Canon" in item for item in warnings))

    def test_v18_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.8"))
        self.assertEqual([], errors)
        self.assertTrue(any("建议升级到 1.9" in item for item in warnings))

    def test_v17_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.7"))
        self.assertEqual([], errors)
        self.assertTrue(any("建议升级到 1.9" in item for item in warnings))

    def test_v16_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.6"))
        self.assertEqual([], errors)
        self.assertTrue(any("建议升级到 1.9" in item for item in warnings))

    def test_v15_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.5"))
        self.assertEqual([], errors)
        self.assertTrue(any("兼容格式" in item for item in warnings))

    def test_v14_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.4"))
        self.assertEqual([], errors)
        self.assertTrue(any("兼容格式" in item for item in warnings))

    def test_v13_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.3"))
        self.assertEqual([], errors)
        self.assertTrue(any("兼容格式" in item for item in warnings))

    def test_v12_is_compatible_with_warning(self) -> None:
        errors, warnings = validate(legacy_state("1.2"))
        self.assertEqual([], errors)
        self.assertTrue(any("兼容格式" in item for item in warnings))

    def test_v11_is_compatible_with_warning(self) -> None:
        state = legacy_state("1.1")
        for field in (
            "task_mode",
            "interaction_state",
            "model_profile",
            "rhythm_profile",
            "specialist_tasks",
        ):
            state.pop(field)
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertTrue(any("兼容格式" in item for item in warnings))

    def test_collaboration_sheet_fields_are_rejected(self) -> None:
        state = template()
        state["google_sheet"] = {"spreadsheet_id": "external-only"}
        state["watermarked_delivery"] = "approved"
        errors, _ = validate(state)
        self.assertTrue(any("外部协作表字段" in item for item in errors))

    def test_confirmed_twenty_year_old_adult_profile_passes(self) -> None:
        errors, warnings = validate(adult_intimacy_state())
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_adult_profile_rejects_age_consent_and_youth_coding_failures(self) -> None:
        state = adult_intimacy_state()
        intimacy = state["content_profile"]["intimacy"]
        intimacy["participants"][0]["age_years"] = 17
        intimacy["consent_status"] = "unclear"
        intimacy["youth_coding"] = True
        errors, _ = validate(state)
        self.assertTrue(any("age_years" in item for item in errors))
        self.assertTrue(any("持续且可撤回" in item for item in errors))
        self.assertTrue(any("校园/幼态编码" in item for item in errors))

    def test_adult_profile_rejects_unverified_source(self) -> None:
        state = adult_intimacy_state()
        state["content_profile"]["intimacy"]["participants"][0][
            "source_authorization"
        ] = "unknown_real_person"
        errors, _ = validate(state)
        self.assertTrue(any("来源未获授权" in item for item in errors))

    def test_mixed_routes_bind_each_lane_to_its_model(self) -> None:
        state = adult_intimacy_state()
        state["approval_gates"]["script_adaptation"]["status"] = "not_required"
        normal = {
            "id": "SEG-N01",
            "mode": "drama",
            "content_lane": "normal",
            "target_model": "seedance-2.5",
            "source_span_ids": ["SPAN-N01"],
            "duration_seconds": 12,
            "dramatic_unit": "正常剧情完成一次关系变化",
            "duration_rationale": "按对白和动作试演估算",
            "shot_count_rationale": "单镜足以承载",
            "rhythm_pacing": state["rhythm_profile"]["pacing"],
            "action_types": [],
            "shots": [{"number": 1, "start": 0, "end": 12, "asset_ids": []}],
            "start_state": "A",
            "end_state": "B",
        }
        adult = {
            "id": "SEG-A01",
            "mode": "drama",
            "content_lane": "adult",
            "target_model": "wan3.0",
            "source_span_ids": ["SPAN-A01"],
            "duration_seconds": 30,
            "dramatic_unit": "已批准成人动作单元",
            "duration_rationale": "按动作、回应和声音试演估算",
            "shot_count_rationale": "连续动作由一个长镜头承载",
            "rhythm_pacing": state["rhythm_profile"]["pacing"],
            "action_types": [],
            "shots": [{"number": 1, "start": 0, "end": 30, "asset_ids": []}],
            "start_state": "B",
            "end_state": "C",
        }
        enrich_segment(normal, "normal")
        enrich_segment(adult, "adult")
        adult["intimacy_beats"] = [intimacy_beat("SPAN-A01", 30)]
        normal["outgoing_transition_id"] = "TR-001"
        adult["incoming_transition_id"] = "TR-001"
        state["segments"] = [normal, adult]
        state["source_span_ledger"] = [
            {
                "id": "SPAN-N01",
                "source_order": 1,
                "source_locator": "测试原文第1段",
                "lane": "normal",
                "status": "routed",
                "segment_id": "SEG-N01",
            },
            {
                "id": "SPAN-A01",
                "source_order": 2,
                "source_locator": "测试原文第2段",
                "lane": "adult",
                "status": "routed",
                "segment_id": "SEG-A01",
            },
        ]
        state["transition_ledger"] = [
            {
                "id": "TR-001",
                "from_segment_id": "SEG-N01",
                "to_segment_id": "SEG-A01",
                "source_span_ids": ["SPAN-N01", "SPAN-A01"],
                "lane_change": "normal_to_adult",
                "completed_meaning": normal["narrative_paragraph"]["meaning"],
                "forward_impulse": normal["narrative_paragraph"]["forward_impulse"],
                "reentry_anchor": adult["reentry_plan"]["anchor"],
                "inherited_state": adult["reentry_plan"]["inherited_state"],
                "edit_bridge": {
                    "match_basis": ["gaze"],
                    "bridge": "gaze-match",
                    "reason": "把正常段确认的关系意图交给成人段的新行动",
                    "intentional_break": False,
                },
                "assembly_contract": {
                    "join_mode": "straight-cut",
                    "visual_join": "正常段的关系确认直接成为成人段已批准行动的起点",
                    "sound_join": "两段共享同一空间底声并在靠近动作落点直切",
                    "combined_meaning": "关系意图从口头与距离变化转为双方明确回应的行动",
                },
                "lighting_change_trigger": None,
                "shared_boundary_asset_id": None,
                "handoff_mode": "state_only",
                "boundary_action": {
                    "outgoing_event": "停在最后一个非明确靠近动作",
                    "incoming_event": adult["reentry_plan"]["opening_action"],
                    "handoff_rule": "non_overlapping_sequential",
                },
                "status": "planned",
            }
        ]
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

        state["segments"][1]["target_model"] = "seedance-2.5"
        errors, _ = validate(state)
        self.assertTrue(any("adult 路必须指向 wan3.0" in item for item in errors))

    def test_forward_pure_normal_emotional_scene_passes(self) -> None:
        state = sequence_state(["normal"], [14])
        state["segments"][0]["performance_arc"].update(
            {
                "trigger": "对方把钥匙放回桌面",
                "dominant_emotion": "强装镇定",
                "secondary_leak": "手指没有立刻松开杯沿",
                "active_tracks": ["gaze", "hands_objects", "breathing_sound"],
                "residual_state": "呼吸变浅，手指压力仍在",
            }
        )
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_forward_normal_adult_normal_bridge_passes(self) -> None:
        state = sequence_state(["normal", "adult", "normal"], [10, 24, 7])
        state["segments"][1]["reentry_plan"]["opening_action"] = (
            "成人段从原文第一个明确且已批准的接触启动"
        )
        state["segments"][2]["reentry_plan"]["opening_action"] = (
            "正常段从暂停结果与未平复呼吸继续"
        )
        state["transition_ledger"][0]["boundary_action"] = {
            "outgoing_event": "正常段停在双方明确注视并相向靠近",
            "incoming_event": state["segments"][1]["reentry_plan"]["opening_action"],
            "handoff_rule": "non_overlapping_sequential",
        }
        state["transition_ledger"][1]["boundary_action"] = {
            "outgoing_event": "成人段在双方主动暂停后停稳",
            "incoming_event": state["segments"][2]["reentry_plan"]["opening_action"],
            "handoff_rule": "non_overlapping_sequential",
        }
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_forward_short_adult_final_segment_keeps_actual_duration(self) -> None:
        state = sequence_state(["adult"], [8.5])
        self.assertEqual(8.5, state["segments"][0]["intimacy_beats"][0]["end"])
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_narrative_paragraph_and_reentry_plan_are_required(self) -> None:
        state = sequence_state(["normal"])
        state["segments"][0].pop("narrative_paragraph")
        state["segments"][0].pop("reentry_plan")
        errors, _ = validate(state)
        self.assertTrue(any("缺少 narrative_paragraph" in item for item in errors))
        self.assertTrue(any("缺少 reentry_plan" in item for item in errors))

    def test_viewpoint_turn_requires_story_revelation(self) -> None:
        state = sequence_state(["normal"])
        state["segments"][0]["camera_plan"]["viewpoint_turns"][0][
            "revealed_meaning"
        ] = ""
        errors, _ = validate(state)
        self.assertTrue(any("revealed_meaning" in item for item in errors))

    def test_reentry_can_change_camera_position_without_resetting_story_world(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["segments"][0]["camera_plan"]["closing_view"] = (
            "从门边看见人物已经接受谈话结果"
        )
        state["segments"][1]["camera_plan"]["entry_view"] = (
            "从桌上仍在震动的手机重新找到人物的新动作"
        )
        state["segments"][1]["reentry_plan"].update(
            {
                "anchor": "桌上仍在震动的手机",
                "first_new_information": "人物没有接电话，而是把钥匙推向对方",
            }
        )
        state["transition_ledger"][0]["reentry_anchor"] = (
            state["segments"][1]["reentry_plan"]["anchor"]
        )
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_transition_semantics_must_match_adjacent_paragraphs(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["transition_ledger"][0]["completed_meaning"] = "另一个未发生的结果"
        state["transition_ledger"][0]["reentry_anchor"] = "不存在的物体"
        errors, _ = validate(state)
        self.assertTrue(any("completed_meaning" in item for item in errors))
        self.assertTrue(any("reentry_anchor" in item for item in errors))

    def test_related_normal_paragraphs_may_share_one_storyboard_asset(self) -> None:
        state = sequence_state(["normal", "normal"])
        for segment in state["segments"]:
            segment["storyboard_asset_ids"] = ["BOARD-01"]
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_adult_reentry_state_cannot_silently_reset(self) -> None:
        state = sequence_state(["adult", "adult"])
        state["segments"][1]["reentry_plan"]["inherited_state"] = (
            "人物身份连续，但服装、支撑、呼吸和同意状态全部重置"
        )
        errors, _ = validate(state)
        self.assertTrue(any("inherited_state" in item for item in errors))

    def test_generation_units_depend_on_canonical_assets_not_previous_clip(self) -> None:
        state = template()
        state["production_rules"]["generation_dependency_policy"] = (
            "extend_previous_generated_clip"
        )
        errors, _ = validate(state)
        self.assertTrue(any("generation_dependency_policy" in item for item in errors))

    def test_v17_requires_exactly_one_transition_for_adjacent_segments(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["transition_ledger"] = []
        errors, _ = validate(state)
        self.assertTrue(any("必须且只能有一个转场" in item for item in errors))

    def test_transition_rejects_wrong_reference_and_lane_change(self) -> None:
        state = sequence_state(["normal", "adult"])
        transition = state["transition_ledger"][0]
        transition["source_span_ids"] = ["SPAN-MISSING"]
        transition["lane_change"] = "same_lane"
        errors, _ = validate(state)
        self.assertTrue(any("引用了无效原文跨度" in item for item in errors))
        self.assertTrue(any("lane_change 应为 normal_to_adult" in item for item in errors))

        state = sequence_state(["normal", "adult"])
        state["segments"][1]["incoming_transition_id"] = "TR-MISSING"
        errors, _ = validate(state)
        self.assertTrue(any("incoming_transition_id" in item for item in errors))

    def test_adult_segment_requires_intimacy_beats(self) -> None:
        state = sequence_state(["adult"])
        state["segments"][0].pop("intimacy_beats")
        errors, _ = validate(state)
        self.assertTrue(any("缺少 intimacy_beats" in item for item in errors))

    def test_lighting_change_requires_local_and_cross_segment_motivation(self) -> None:
        state = sequence_state(["normal", "normal"])
        segment = state["segments"][0]
        segment["lighting_state"]["end"]["key_direction"] = "画面右侧"
        errors, _ = validate(state)
        self.assertTrue(any("缺少 change_trigger" in item for item in errors))
        self.assertTrue(any("缺少 lighting_change_trigger" in item for item in errors))

    def test_transition_rejects_duplicate_boundary_action(self) -> None:
        state = sequence_state(["normal", "adult"])
        boundary = state["transition_ledger"][0]["boundary_action"]
        boundary["incoming_event"] = boundary["outgoing_event"]
        errors, _ = validate(state)
        self.assertTrue(any("边界动作重复" in item for item in errors))

    def test_adult_beat_requires_response_support_coverage_consent_and_end_state(self) -> None:
        state = sequence_state(["adult"], [9])
        beat = state["segments"][0]["intimacy_beats"][0]
        beat["response"] = "unclear"
        beat["support_map"] = []
        beat["coverage_after"] = ""
        beat["consent_checkpoint"] = ""
        beat["end_state"] = ""
        errors, _ = validate(state)
        self.assertTrue(any("response 必须明确且可撤回" in item for item in errors))
        self.assertTrue(any("support_map 不能为空" in item for item in errors))
        self.assertTrue(any("coverage_after" in item for item in errors))
        self.assertTrue(any("consent_checkpoint" in item for item in errors))
        self.assertTrue(any("end_state" in item for item in errors))

    def test_adult_beat_rejects_time_gap_and_duplicate_source_span(self) -> None:
        state = sequence_state(["adult"], [10])
        first = state["segments"][0]["intimacy_beats"][0]
        first["end"] = 4
        second = copy.deepcopy(first)
        second.update({"id": "IB-002", "start": 5, "end": 10})
        state["segments"][0]["intimacy_beats"].append(second)
        errors, _ = validate(state)
        self.assertTrue(any("起点不连续" in item for item in errors))
        self.assertTrue(any("同一原文动作跨度" in item for item in errors))

    def test_lane_specific_storyboard_and_intimacy_fields_are_enforced(self) -> None:
        normal_state = sequence_state(["normal"])
        normal_state["segments"][0]["intimacy_beats"] = [
            intimacy_beat("SPAN-01", 12)
        ]
        normal_errors, _ = validate(normal_state)
        self.assertTrue(any("正常片段" in item and "intimacy_beats" in item for item in normal_errors))

        adult_state = sequence_state(["adult"])
        adult_state["segments"][0]["storyboard_asset_ids"] = ["BOARD-A01"]
        adult_errors, _ = validate(adult_state)
        self.assertTrue(any("不得绑定十六宫格" in item for item in adult_errors))

    def test_shared_boundary_keyframe_must_exist_and_be_approved(self) -> None:
        state = sequence_state(["normal", "adult"])
        transition = state["transition_ledger"][0]
        transition.update(
            {
                "handoff_mode": "shared_boundary_keyframe",
                "shared_boundary_asset_id": "KEY-BOUNDARY-01",
                "status": "approved",
            }
        )
        errors, _ = validate(state)
        self.assertTrue(any("不存在的共享边界资产" in item for item in errors))

        state["assets"] = [
            {
                "id": "KEY-BOUNDARY-01",
                "status": "planned",
                "responsibility": "跨模型中性边界关键帧",
            }
        ]
        errors, _ = validate(state)
        self.assertTrue(any("共享边界资产尚未 approved" in item for item in errors))

    def test_performance_camera_lighting_transition_changes_reset_g2_to_g7(self) -> None:
        for change_type in ("performance", "cinematography", "lighting", "transition"):
            with self.subTest(change_type=change_type):
                state = template()
                for gate in state["approval_gates"].values():
                    gate["status"] = "approved"
                    gate["approved_revision"] = 1
                state["adapted_script"].update(
                    {
                        "status": "approved",
                        "approved_revision": 1,
                        "source_revision": 1,
                        "scene_ids": ["SCENE-01"],
                    }
                )
                apply_change(state, change_type, "用户批准修改 Canon")
                self.assertEqual(2, state["revision"])
                self.assertEqual("approved", state["approval_gates"]["script_adaptation"]["status"])
                self.assertEqual(2, state["approval_gates"]["script_adaptation"]["approved_revision"])
                self.assertTrue(
                    all(
                        state["approval_gates"][name]["status"] == "pending"
                        for name in GATE_ORDER[1:]
                    )
                )
                self.assertEqual("G2", state["stage"])

    def test_full_project_waiting_at_g1_cannot_approve_downstream(self) -> None:
        state = template()
        state["approval_gates"]["script_adaptation"]["status"] = "awaiting_confirmation"
        state["approval_gates"]["shot_breakdown"] = {
            "status": "approved",
            "approved_revision": 1,
            "note": "",
        }
        state["interaction_state"]["pending_gate"] = "script_adaptation"
        errors, _ = validate(state)
        self.assertTrue(any("shot_breakdown 已完成" in item for item in errors))

    def test_continue_approves_only_unique_waiting_gate(self) -> None:
        state = template()
        state["approval_gates"]["script_adaptation"]["status"] = "awaiting_confirmation"
        state["interaction_state"]["pending_gate"] = "script_adaptation"
        approved = approve_pending_gate(state)
        self.assertEqual("script_adaptation", approved)
        self.assertEqual("approved", state["approval_gates"]["script_adaptation"]["status"])
        self.assertEqual("pending", state["approval_gates"]["shot_breakdown"]["status"])
        self.assertIsNone(state["interaction_state"]["pending_gate"])

    def test_specialist_diagnostic_does_not_create_core_approvals(self) -> None:
        state = template()
        state["task_mode"] = "specialist"
        state["interaction_state"]["current_stage"] = "specialist"
        state["specialist_tasks"] = [specialist_task()]
        before = copy.deepcopy(state["approval_gates"])
        errors, _ = validate(state)
        self.assertEqual([], errors)
        self.assertEqual(before, state["approval_gates"])

    def test_dialogue_finding_requires_evidence_and_speech_risk(self) -> None:
        state = template()
        state["task_mode"] = "specialist"
        state["interaction_state"]["current_stage"] = "specialist"
        task = specialist_task("dialogue_polish")
        task["findings"][0]["evidence"] = ""
        task.pop("natural_speech_risk")
        state["specialist_tasks"] = [task]
        errors, _ = validate(state)
        self.assertTrue(any("缺少 evidence" in item for item in errors))
        self.assertTrue(any("natural_speech_risk" in item for item in errors))

    def test_dialogue_and_rhythm_application_reset_all_gates(self) -> None:
        for change_type in ("dialogue", "rhythm"):
            with self.subTest(change_type=change_type):
                state = template()
                for gate in state["approval_gates"].values():
                    gate["status"] = "approved"
                    gate["approved_revision"] = 1
                apply_change(state, change_type, "用户批准应用")
                self.assertEqual(2, state["revision"])
                self.assertTrue(
                    all(state["approval_gates"][name]["status"] == "pending" for name in GATE_ORDER)
                )
                self.assertEqual(2, state["adapted_script"]["source_revision"])

    def test_performance_specialist_requires_traceable_arc_contract(self) -> None:
        state = template()
        state["task_mode"] = "specialist"
        state["interaction_state"]["current_stage"] = "specialist"
        task = specialist_task("performance_design")
        state["specialist_tasks"] = [task]
        errors, _ = validate(state)
        self.assertEqual([], errors)

        task["performance_scope"]["source_span_ids"] = []
        task["proposed_performance_arcs"][0]["active_tracks"] = ["fixed_face_quota"]
        errors, _ = validate(state)
        self.assertTrue(any("至少需要一个 source_span_id" in item for item in errors))
        self.assertTrue(any("无效表演轨" in item for item in errors))

    def test_post_sound_prompt_reopens_only_g7(self) -> None:
        state = template()
        for gate in state["approval_gates"].values():
            gate["status"] = "approved"
            gate["approved_revision"] = 1
        apply_change(state, "post_sound_prompt", "调整生成内声音")
        self.assertEqual(1, state["revision"])
        self.assertEqual("pending", state["approval_gates"]["final_compile"]["status"])
        self.assertTrue(
            all(state["approval_gates"][name]["status"] == "approved" for name in GATE_ORDER[:-1])
        )

    def test_action_route_rejects_more_than_two_types(self) -> None:
        state = template()
        state["approval_gates"]["script_adaptation"]["status"] = "not_required"
        attach_segment(
            state,
            {
                "id": "SEG-01",
                "mode": "action",
                "duration_seconds": 25,
                "dramatic_unit": "一次战术交换",
                "duration_rationale": "按动作试演估算",
                "shot_count_rationale": "测试动作类型路由",
                "rhythm_pacing": "high_density_hook_action",
                "rhythm_exception_reason": "战斗高潮",
                "action_types": ["free_combat", "wuxia_weapons", "superpower"],
                "shots": [],
                "start_state": "A",
                "end_state": "B",
            },
        )
        errors, _ = validate(state)
        self.assertTrue(any("混合动作类型最多两个" in item for item in errors))

    def test_adaptive_one_take_and_short_scene_pass(self) -> None:
        for mode, duration in (("drama", 12), ("drama", 30), ("action", 8)):
            with self.subTest(mode=mode, duration=duration):
                state = template()
                state["approval_gates"]["script_adaptation"]["status"] = "not_required"
                attach_segment(
                    state,
                    {
                        "id": "SEG-01",
                        "mode": mode,
                        "duration_seconds": duration,
                        "dramatic_unit": "人物完成一次不可逆的选择",
                        "duration_rationale": "按对白、停顿和动作试演估算",
                        "shot_count_rationale": "单一机位能完整承载表演，不切镜",
                        "rhythm_pacing": state["rhythm_profile"]["pacing"],
                        "action_types": ["free_combat"] if mode == "action" else [],
                        "shots": [
                            {
                                "number": 1,
                                "start": 0,
                                "end": duration,
                                "asset_ids": [],
                            }
                        ],
                        "start_state": "A",
                        "end_state": "B",
                    },
                )
                errors, _ = validate(state)
                self.assertEqual([], errors)

    def test_segment_over_model_limit_is_rejected(self) -> None:
        state = template()
        state["approval_gates"]["script_adaptation"]["status"] = "not_required"
        attach_segment(
            state,
            {
                "id": "SEG-01",
                "mode": "drama",
                "duration_seconds": 31,
                "dramatic_unit": "一次关系变化",
                "duration_rationale": "错误测试",
                "shot_count_rationale": "单镜",
                "rhythm_pacing": state["rhythm_profile"]["pacing"],
                "action_types": [],
                "shots": [{"number": 1, "start": 0, "end": 31, "asset_ids": []}],
                "start_state": "A",
                "end_state": "B",
            },
        )
        errors, _ = validate(state)
        self.assertTrue(any("超过有效上限" in item for item in errors))

    def test_post_sound_cue_contract_and_bgm_boundary(self) -> None:
        state = template()
        state["task_mode"] = "specialist"
        state["interaction_state"]["current_stage"] = "specialist"
        task = specialist_task("post_sound")
        state["specialist_tasks"] = [task]
        errors, _ = validate(state)
        self.assertEqual([], errors)

        task["writes_to_seedance_prompt"] = True
        task["cue_sheet"][0]["silence"] = ""
        errors, _ = validate(state)
        self.assertTrue(any("后期BGM不得写入" in item for item in errors))
        self.assertTrue(any("缺少 silence" in item for item in errors))

    def test_reference_limits_for_all_modalities_and_fake_reference(self) -> None:
        state = template()
        for gate in state["approval_gates"].values():
            gate["status"] = "approved"
            gate["approved_revision"] = 1
        state["adapted_script"].update(
            {"status": "approved", "approved_revision": 1, "scene_ids": ["SCENE-01"]}
        )
        state["assets"] = [
            {
                "id": f"ASSET-{index:02d}",
                "status": "approved",
                "responsibility": "测试引用上限",
                "attachment_ref": f"@图片{index}",
            }
            for index in range(1, 32)
        ]
        state["assets"].append(
            {
                "id": "ASSET-FAKE",
                "status": "approved",
                "responsibility": "错误格式",
                "attachment_ref": "@图片0",
            }
        )
        errors, _ = validate(state)
        self.assertTrue(any("images引用数量 31" in item for item in errors))
        self.assertTrue(any("attachment_ref 格式无效" in item for item in errors))

        for label, limit_key, count in (("视频", "videos", 11), ("音频", "audios", 11)):
            with self.subTest(modality=label):
                modality_state = template()
                for gate in modality_state["approval_gates"].values():
                    gate["status"] = "approved"
                    gate["approved_revision"] = 1
                modality_state["adapted_script"].update(
                    {"status": "approved", "approved_revision": 1, "scene_ids": ["SCENE-01"]}
                )
                modality_state["assets"] = [
                    {
                        "id": f"{limit_key.upper()}-{index:02d}",
                        "status": "approved",
                        "responsibility": "测试引用上限",
                        "attachment_ref": f"@{label}{index}",
                    }
                    for index in range(1, count + 1)
                ]
                modality_errors, _ = validate(modality_state)
                self.assertTrue(
                    any(f"{limit_key}引用数量 {count}" in item for item in modality_errors)
                )

    def test_v19_requires_concrete_composition_and_camera_trigger(self) -> None:
        state = sequence_state(["normal"])
        state["segments"][0]["composition_plan"]["dominant_point"] = "电影感"
        state["segments"][0]["camera_plan"]["viewpoint_turns"][0]["trigger"] = ""
        errors, _ = validate(state)
        self.assertTrue(any("真实空间关系" in item for item in errors))
        self.assertTrue(any("viewpoint_turns[0].trigger" in item for item in errors))

    def test_v19_all_motion_state_pairs_are_allowed(self) -> None:
        for outgoing, incoming in (
            ("moving", "moving"),
            ("static", "static"),
            ("static", "moving"),
            ("moving", "static"),
        ):
            with self.subTest(outgoing=outgoing, incoming=incoming):
                state = sequence_state(["normal", "normal"])
                state["segments"][0]["camera_plan"]["continuity"]["motion_out"] = outgoing
                state["segments"][1]["camera_plan"]["continuity"]["motion_in"] = incoming
                errors, _ = validate(state)
                self.assertEqual([], errors)

    def test_v19_continuity_may_be_not_applicable(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["segments"][0]["camera_plan"]["continuity"] = "not-applicable"
        state["segments"][1]["camera_plan"]["continuity"] = "not-applicable"
        errors, _ = validate(state)
        self.assertEqual([], errors)

    def test_v19_rejects_meaningless_assembly_meaning(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["transition_ledger"][0]["assembly_contract"]["combined_meaning"] = "过渡"
        errors, _ = validate(state)
        self.assertTrue(any("新增故事意义" in item for item in errors))

    def test_v19_requires_sound_bible(self) -> None:
        state = template()
        del state["sound_bible"]
        errors, _ = validate(state)
        self.assertTrue(any("缺少 sound_bible" in item for item in errors))

    def test_v19_requires_chinese_short_drama_script_format(self) -> None:
        state = template()
        state["production_rules"]["script_format"] = "generic_markdown"
        errors, _ = validate(state)
        self.assertTrue(any("集数-场次格式" in item for item in errors))

    def test_v19_five_montage_relations_add_meaning(self) -> None:
        for relation in (
            "narrative-compression",
            "rhythm",
            "contrast",
            "parallel",
            "expressive",
        ):
            with self.subTest(relation=relation):
                state = sequence_state(["normal", "normal"])
                state["transition_ledger"][0]["assembly_contract"].update(
                    {
                        "join_mode": "montage-cut",
                        "montage_relation": relation,
                        "combined_meaning": f"{relation} 让前段结果改变后段选择的理解",
                    }
                )
                errors, _ = validate(state)
                self.assertEqual([], errors)

    def test_v19_cross_unit_jl_overlap_is_rejected(self) -> None:
        state = sequence_state(["normal", "normal"])
        state["transition_ledger"][0]["assembly_contract"]["sound_join"] = (
            "使用 J/L 声音预入覆盖两个独立文件"
        )
        errors, _ = validate(state)
        self.assertTrue(any("J/L 音轨重叠" in item for item in errors))

    def test_v19_rejects_fixed_shot_formula_and_prompt_opening(self) -> None:
        state = sequence_state(["normal"])
        state["segments"][0]["shot_count_rationale"] = "凑够远中近"
        text = "远中近：人物走入房间并坐下。"
        state["compiled_prompts"] = [
            {
                "id": "PROMPT-FORMULA",
                "segment_id": "SEG-01",
                "target_model": "seedance-2.5",
                "text": text,
                "character_count": count_prompt_characters(text),
                "compiled_revision": 1,
            }
        ]
        errors, _ = validate(state)
        self.assertTrue(any("固定景别或强制运镜公式" in item for item in errors))
        self.assertTrue(any("不得以镜头字段或时长参数开头" in item for item in errors))

    def test_v19_reaction_then_reveal_and_attention_carrier_pass(self) -> None:
        state = sequence_state(["normal"])
        segment = state["segments"][0]
        segment["camera_plan"]["attention_progression"] = (
            "注意力先停在人物听见异响后的反应，再沿她的视线找到门后的湿雨伞"
        )
        segment["camera_plan"]["viewpoint_turns"][0].update(
            {
                "trigger": "人物先停下动作并看向门后",
                "camera_response": "观看随后越过她的肩膀找到尚在滴水的雨伞",
                "revealed_meaning": "观众在反应成立后才知道有人刚刚进入",
            }
        )
        errors, _ = validate(state)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
