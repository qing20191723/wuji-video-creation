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
    validate,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_ROOT / "assets" / "project-state.template.json"


def template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def legacy_state(version: str) -> dict:
    state = template()
    state["schema_version"] = version
    state["production_rules"].update(
        {"drama_segment_seconds": 30, "action_segment_seconds": 25}
    )
    state["rhythm_profile"].update(
        {"hook_window_seconds": [0, 5], "progression_interval_seconds": 15}
    )
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


def attach_segment(state: dict, segment: dict, lane: str = "normal") -> None:
    span_id = f"SPAN-{segment['id']}"
    segment["content_lane"] = lane
    segment["target_model"] = "seedance-2.5" if lane == "normal" else "wan3.0"
    segment["source_span_ids"] = [span_id]
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
    def test_v15_template_passes(self) -> None:
        errors, warnings = validate(template())
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

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
        errors, warnings = validate(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

        state["segments"][1]["target_model"] = "seedance-2.5"
        errors, _ = validate(state)
        self.assertTrue(any("adult 路必须指向 wan3.0" in item for item in errors))

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


if __name__ == "__main__":
    unittest.main()
