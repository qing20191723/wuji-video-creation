"""Versioned film artifacts, scoped dependency invalidation and four review gates.

Standard library only. All mutations return copies; callers save explicitly.
Approval evidence is an audit record of user input, not an authentication system.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("script", "shot_plan", "assets", "storyboard", "compile")
KIND_STAGE = dict(scene="script", shot="shot_plan", asset="assets", board="storyboard",
                  unit="compile", prompt="compile")
ASPECTS = ("story", "dialogue", "performance", "visual", "timing", "sound", "wording")
CHANGES = {
    "story": ASPECTS, "dialogue": ("dialogue", "performance", "timing", "sound"),
    "performance": ("performance", "visual", "timing"), "visual": ("visual",),
    "timing": ("timing", "sound"), "sound": ("sound",), "wording": ("wording",),
}
STATUSES = {"draft", "ready", "awaiting_confirmation", "approved", "stale", "blocked"}


def now():
    return datetime.now(timezone.utc).isoformat()


def positive(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def new_state(project_id="PROJECT-001", aspect="16:9"):
    return dict(schema_version="2.0", project_id=project_id, revision=1,
                task_mode="full_production", stage="script", format=aspect,
                source_lock={"confirmed_facts": [], "forbidden_changes": [], "allowed_inferences": []},
                artifacts=[], pending_review=None, approvals=[], change_log=[],
                specialist_tasks=[], model_profiles=[],
                delivery={"endpoint": "images_and_video_prompts", "status": "draft"})


def new_artifact(artifact_id, kind, content, dependencies=()):
    return dict(id=artifact_id, kind=kind, version=1, status="draft", content=copy.deepcopy(content),
                aspect_versions={key: 1 for key in ASPECTS}, approved_version=None,
                depends_on=copy.deepcopy(list(dependencies)))


def dependency(artifact, uses=ASPECTS):
    if not uses or set(uses) - set(ASPECTS):
        raise ValueError("Dependency requires known aspects")
    return {"id": artifact["id"], "versions": {key: artifact["aspect_versions"][key] for key in uses}}


def digest(artifact):
    payload = {key: artifact.get(key) for key in ("id", "kind", "version", "aspect_versions", "content", "depends_on", "media")}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def index(data):
    return {a["id"]: a for a in data["artifacts"]}


def _current(artifact, items):
    return all(dep["id"] in items and all(items[dep["id"]]["aspect_versions"].get(k) == v
               for k, v in dep["versions"].items()) for dep in artifact["depends_on"])


def _attested(dep, data, items):
    target = items[dep["id"]]
    if target["kind"] in ("unit", "prompt"):
        return target["status"] == "ready"
    # Unchanged visual facts can retain approval while a dialogue revision is pending.
    return any(all(record.get("aspects", {}).get(k) == v for k, v in dep["versions"].items())
               for approval in data["approvals"] for record in approval.get("items", [])
               if record.get("id") == target["id"] and approval.get("source") == "user"
               and approval.get("stage") == KIND_STAGE[target["kind"]])


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["State must be an object"], warnings
    if data.get("schema_version") != "2.0":
        errors.append("Expected schema_version 2.0")
    if not positive(data.get("revision")) or not isinstance(data.get("project_id"), str) or not data.get("project_id"):
        errors.append("project_id and positive revision required")
    if not isinstance(data.get("source_lock"), dict):
        errors.append("source_lock must be an object")
    if data.get("stage") not in STAGES:
        errors.append("Unknown stage")
    if data.get("task_mode") not in ("full_production", "specialist"):
        errors.append("Unknown task_mode")
    if not re.fullmatch(r"[1-9]\d*:[1-9]\d*", str(data.get("format", ""))):
        errors.append("format must be a positive aspect ratio")
    for field in ("artifacts", "approvals", "change_log", "specialist_tasks", "model_profiles"):
        if not isinstance(data.get(field), list):
            errors.append(f"{field} must be a list")
    if errors:
        return errors, warnings
    items = {}
    for a in data["artifacts"]:
        if not isinstance(a, dict) or not isinstance(a.get("id"), str) or not a["id"]:
            errors.append("Each artifact needs a stable string ID")
            continue
        aid = a["id"]
        if aid in items:
            errors.append(f"Duplicate artifact ID: {aid}")
        items[aid] = a
        if a.get("kind") not in KIND_STAGE or a.get("status") not in STATUSES:
            errors.append(f"{aid}: unknown kind/status")
        if not positive(a.get("version")) or not isinstance(a.get("content"), dict):
            errors.append(f"{aid}: invalid version/content")
        av = a.get("aspect_versions")
        if not isinstance(av, dict) or set(av) != set(ASPECTS) or not all(positive(v) for v in av.values()):
            errors.append(f"{aid}: invalid aspect_versions")
        deps = a.get("depends_on")
        if not isinstance(deps, list):
            errors.append(f"{aid}: depends_on must be a list")
            continue
        seen = set()
        for dep in deps:
            if not isinstance(dep, dict) or not isinstance(dep.get("id"), str):
                errors.append(f"{aid}: invalid dependency")
                continue
            versions = dep.get("versions")
            if (dep["id"] in seen or not isinstance(versions, dict) or not versions
                    or set(versions) - set(ASPECTS) or not all(positive(v) for v in versions.values())):
                errors.append(f"{aid}: invalid dependency versions/duplicate dependency")
            seen.add(dep["id"])
    if errors:
        return errors, warnings
    for a in items.values():
        for dep in a["depends_on"]:
            if dep["id"] not in items:
                errors.append(f"{a['id']}: unknown dependency {dep['id']}")
    if errors:
        return errors, warnings
    visiting, visited = set(), set()
    def visit(aid):
        if aid in visiting:
            errors.append(f"Dependency cycle: {aid}")
            return
        if aid in visited:
            return
        visiting.add(aid)
        for dep in items[aid]["depends_on"]:
            visit(dep["id"])
        visiting.remove(aid)
        visited.add(aid)
    for aid in items:
        visit(aid)
    for approval in data["approvals"]:
        if (not isinstance(approval, dict) or approval.get("source") != "user"
                or approval.get("stage") not in STAGES[:4] or not approval.get("evidence")
                or not approval.get("at") or not isinstance(approval.get("items"), list)
                or not all(isinstance(r, dict) and isinstance(r.get("aspects"), dict)
                           for r in approval.get("items", []))):
            errors.append("Invalid approval record; preserve legacy records under legacy_snapshot")
    if errors:
        return errors, warnings
    for a in items.values():
        aid, kind, content = a["id"], a["kind"], a["content"]
        active = a["status"] in ("ready", "awaiting_confirmation", "approved")
        for approval in data["approvals"]:
            for record in approval["items"]:
                if record.get("id") == aid and record.get("version") == a["version"] and record.get("digest") != digest(a):
                    errors.append(f"{aid}: previously reviewed version changed without version increment")
        if kind == "asset":
            uses = content.get("used_by", [])
            if not isinstance(uses, list) or any(not isinstance(sid, str) or sid not in items or items[sid]["kind"] != "shot" for sid in uses):
                errors.append(f"{aid}: used_by must reference existing shots")
        if active and not _current(a, items):
            errors.append(f"{aid}: stale dependency versions")
        if active and not all(_attested(dep, data, items) for dep in a["depends_on"]):
            errors.append(f"{aid}: dependencies lack relevant approval/readiness")
        if a["status"] == "approved":
            matching = [r for approval in data["approvals"] if approval["stage"] == KIND_STAGE[kind]
                        for r in approval["items"] if r.get("id") == aid and r.get("version") == a["version"]
                        and r.get("digest") == digest(a) and r.get("aspects") == a["aspect_versions"]]
            if a.get("approved_version") != a["version"] or not matching:
                errors.append(f"{aid}: approval does not bind this artifact version/content")
        elif a.get("approved_version") is not None:
            errors.append(f"{aid}: non-approved artifact has approved_version")
        if not active:
            continue
        dep_kinds = {items[dep["id"]]["kind"] for dep in a["depends_on"]}
        required = {"shot": "scene", "board": "shot", "unit": "shot", "prompt": "unit"}.get(kind)
        if required and required not in dep_kinds:
            errors.append(f"{aid}: requires {required} dependency")
        if kind == "asset" and not dep_kinds.intersection({"scene", "shot", "asset"}):
            errors.append(f"{aid}: asset requires a story/shot/identity dependency")
        fields = {"scene": ("heading", "text"), "shot": ("size", "camera", "action", "sound", "join"),
                  "asset": ("role", "description"), "unit": ("start_state", "end_state", "join"),
                  "prompt": ("text", "profile_id")}.get(kind, ())
        if any(not isinstance(content.get(f), str) or not content[f].strip() for f in fields):
            errors.append(f"{aid}: missing readable {kind} content")
            continue
        if kind in ("asset", "board"):
            media = a.get("media", {})
            if (not isinstance(media, dict) or not media.get("path") or media.get("reviewed") is not True
                    or media.get("reviewed_version") != a["version"] or not media.get("review_note")
                    or not re.fullmatch(r"[0-9a-f]{64}", str(media.get("sha256", "")))):
                errors.append(f"{aid}: actual, visually reviewed image required")
        if kind == "board":
            panels, rows = content.get("panels"), content.get("row_lengths")
            if content.get("style") not in ("black_white_lineart", "color") or content.get("panel_aspect") != data["format"]:
                errors.append(f"{aid}: board requires black_white_lineart or color and project panel aspect")
            if (not isinstance(panels, list) or not panels or not isinstance(rows, list) or not rows
                    or not all(positive(v) for v in rows)):
                errors.append(f"{aid}: panels and positive row_lengths required")
                continue
            if sum(rows) != len(panels) or any(v != rows[0] for v in rows[:-1]) or rows[-1] > rows[0]:
                errors.append(f"{aid}: layout must map every real panel with optional short final row")
            panel_ids = set()
            for panel in panels:
                if not isinstance(panel, dict) or not isinstance(panel.get("id"), str):
                    errors.append(f"{aid}: invalid panel")
                    continue
                if panel["id"] in panel_ids or not panel.get("state"):
                    errors.append(f"{aid}: duplicate panel/empty action state")
                panel_ids.add(panel["id"])
                sid = panel.get("shot_id")
                if not isinstance(sid, str) or sid not in items or items[sid]["kind"] != "shot" or sid not in {d["id"] for d in a["depends_on"]}:
                    errors.append(f"{aid}: panel must map to a directly referenced shot")
        if kind == "unit":
            duration = content.get("duration_seconds")
            if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 < duration < float("inf"):
                errors.append(f"{aid}: positive finite actual duration required")
            if "board" not in dep_kinds and not content.get("board_exception"):
                errors.append(f"{aid}: board dependency or explicit exception required")
        if kind == "prompt":
            _validate_prompt(a, data, items, errors)
    pending = data.get("pending_review")
    waiting = {a["id"] for a in items.values() if a["status"] == "awaiting_confirmation"}
    if pending is not None:
        if (not isinstance(pending, dict) or pending.get("stage") not in STAGES[:4]
                or not isinstance(pending.get("items"), list) or not pending["items"]):
            errors.append("Invalid pending_review")
        else:
            pids = set()
            for r in pending["items"]:
                if not isinstance(r, dict) or not isinstance(r.get("id"), str) or r.get("id") not in items:
                    errors.append("Review refers to unknown artifact")
                    continue
                a = items[r["id"]]
                if (r["id"] in pids or KIND_STAGE[a["kind"]] != pending["stage"]
                        or r.get("version") != a["version"] or r.get("digest") != digest(a)):
                    errors.append("Review must bind exact versions in one stage")
                pids.add(r["id"])
            if pids != waiting:
                errors.append("Pending review and awaiting artifacts differ")
    elif waiting:
        errors.append("Awaiting artifacts require pending_review")
    delivery = data.get("delivery", {})
    if not isinstance(delivery, dict) or delivery.get("endpoint") != "images_and_video_prompts":
        errors.append("Invalid delivery endpoint")
    elif delivery.get("status") not in ("draft", "ready"):
        errors.append("Invalid delivery status")
    elif delivery["status"] == "ready":
        if pending or not items or any(a["status"] != ("ready" if a["kind"] in ("unit", "prompt") else "approved") for a in items.values()):
            errors.append("Delivery requires current approved upstream and ready compilation")
        kinds = {a["kind"] for a in items.values()}
        if not {"scene", "shot", "unit", "prompt"} <= kinds:
            errors.append("Delivery lacks story/shot/unit/prompt coverage")
        covered_shots = {d["id"] for a in items.values() if a["kind"] == "unit" for d in a["depends_on"]}
        for a in items.values():
            if a["kind"] == "shot" and a["id"] not in covered_shots:
                errors.append(f"{a['id']}: shot missing from compilation")
            if a["kind"] == "unit":
                count = sum(any(d["id"] == a["id"] for d in p["depends_on"]) for p in items.values() if p["kind"] == "prompt")
                if count != 1:
                    errors.append(f"{a['id']}: needs exactly one prompt")
    return errors, warnings


def _validate_prompt(a, data, items, errors):
    c, aid = a["content"], a["id"]
    profiles = [p for p in data["model_profiles"] if isinstance(p, dict) and p.get("id") == c.get("profile_id")]
    if len(profiles) != 1:
        errors.append(f"{aid}: unique verified model profile required")
        return
    profile = profiles[0]
    if profile.get("blockers"):
        errors.append(f"{aid}: model entry has unresolved blockers")
    if any(not profile.get(k) for k in ("model", "entry", "verified_at", "source")):
        errors.append(f"{aid}: model entry needs dated verification and source")
    try:
        datetime.fromisoformat(str(profile.get("verified_at", "")))
    except ValueError:
        errors.append(f"{aid}: verification date must be ISO format")
    limits = profile.get("limits", {})
    if not isinstance(limits, dict):
        errors.append(f"{aid}: invalid limits")
        return
    for key in ("duration_seconds", "prompt_characters", "images"):
        limit = limits.get(key)
        if limit is not None and (isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit <= 0):
            errors.append(f"{aid}: invalid {key} limit")
            return
    text = c.get("text", "")
    if limits.get("prompt_characters") and len(text) > limits["prompt_characters"]:
        errors.append(f"{aid}: prompt exceeds verified limit; never truncate")
    deps = {d["id"] for d in a["depends_on"]}
    for depid in deps:
        unit = items[depid]
        if unit["kind"] == "unit" and limits.get("duration_seconds"):
            duration = unit["content"].get("duration_seconds")
            if isinstance(duration, (int, float)) and duration > limits["duration_seconds"]:
                errors.append(f"{aid}: unit exceeds verified duration limit")
    refs = c.get("references")
    if not isinstance(refs, list) or not refs:
        errors.append(f"{aid}: actual image references required")
        return
    names = set()
    for ref in refs:
        if not isinstance(ref, dict) or not isinstance(ref.get("id"), str) or ref.get("id") not in items or not isinstance(ref.get("name"), str):
            errors.append(f"{aid}: unknown reference")
            continue
        target = items[ref["id"]]
        if ref["id"] not in deps or target["kind"] not in ("asset", "board") or not ref.get("name") or ref["name"] in names:
            errors.append(f"{aid}: references must be unique named direct image dependencies")
        names.add(ref.get("name"))
        role = "composition_action" if target["kind"] == "board" else "identity_appearance_space"
        if ref.get("role") != role:
            errors.append(f"{aid}: wrong reference responsibility for {ref['id']}")
    if limits.get("images") and len(refs) > limits["images"]:
        errors.append(f"{aid}: too many images for entry")
    kinds = {items[r['id']]['kind'] for r in refs if isinstance(r, dict) and isinstance(r.get('id'), str) and r.get('id') in items}
    if kinds == {"asset", "board"} and profile.get("supports_combined_refs") is not True:
        errors.append(f"{aid}: combined asset/board references unsupported or unverified")
    if not set(re.findall(r"@图片\d+", text)) <= names:
        errors.append(f"{aid}: fabricated image alias in prompt")


def verify_media(data, base):
    errors = []
    for a in data["artifacts"]:
        if a["kind"] not in ("asset", "board") or a["status"] not in ("ready", "approved", "awaiting_confirmation"):
            continue
        media = a.get("media", {})
        path = Path(base) / str(media.get("path", ""))
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"{a['id']}: image file unavailable: {path}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != media.get("sha256"):
            errors.append(f"{a['id']}: image hash mismatch")
        else:
            header = path.read_bytes()[:16]
            if not (header.startswith(b'\x89PNG\r\n\x1a\n') or header.startswith(b'\xff\xd8\xff')
                    or header[:6] in (b'GIF87a', b'GIF89a') or (header[:4] == b'RIFF' and header[8:12] == b'WEBP')):
                errors.append(f"{a['id']}: unsupported image signature; use PNG/JPEG/GIF/WebP and inspect visually")
    return errors


def require_valid(data, media_base=None):
    errors, _ = validate(data)
    if not errors and media_base is not None:
        errors += verify_media(data, media_base)
    if errors:
        raise ValueError("; ".join(errors))


def apply_change(data, target_ids, change_type, reason):
    require_valid(data)
    result = copy.deepcopy(data)
    items = index(result)
    if change_type not in CHANGES or not reason.strip() or not target_ids or set(target_ids) - items.keys():
        raise ValueError("Known targets, change type and reason required")
    if change_type == "wording" and any(items[i]["kind"] != "prompt" for i in target_ids):
        raise ValueError("wording is only for compiled prompts")
    affected = {aid: set(CHANGES[change_type]) for aid in target_ids}
    changed = True
    while changed:
        changed = False
        for aid, a in items.items():
            impacts = set().union(*(affected.get(d["id"], set()) & d["versions"].keys() for d in a["depends_on"]))
            if impacts and a["kind"] in ("asset", "board"):
                # Any relied-on upstream change can change the rendered result itself.
                impacts.add("visual")
            if a["kind"] == "shot" and any(aid in source["content"].get("used_by", [])
                    and "visual" in affected.get(source["id"], set())
                    for source in items.values() if source["kind"] == "asset"):
                impacts.add("visual")
            if impacts - affected.get(aid, set()):
                affected.setdefault(aid, set()).update(impacts)
                changed = True
    pending = result.get("pending_review")
    if pending and any(r["id"] in affected for r in pending["items"]):
        for r in pending["items"]:
            items[r["id"]]["status"] = "ready"
        result["pending_review"] = None
    for aid, aspects in affected.items():
        a = items[aid]
        a["version"] += 1
        for aspect in aspects:
            a["aspect_versions"][aspect] += 1
        a["status"], a["approved_version"] = "stale", None
        if "media" in a:
            a["media"]["reviewed"] = False
    result["revision"] += 1
    result["stage"] = (result["pending_review"]["stage"] if result["pending_review"] else
                       min((KIND_STAGE[items[i]["kind"]] for i in affected), key=STAGES.index))
    result["delivery"]["status"] = "draft"
    result["change_log"].append(dict(revision=result["revision"], targets=list(target_ids),
                                     change_type=change_type, reason=reason, affected=sorted(affected), at=now()))
    return result


def refresh_dependencies(data, artifact_id):
    """Call only after reworking the artifact against the new upstream content."""
    result = copy.deepcopy(data)
    items = index(result)
    a = items[artifact_id]
    if a["status"] in ("approved", "awaiting_confirmation"):
        raise ValueError("Invalidate before revising an approved artifact")
    for dep in a["depends_on"]:
        dep["versions"] = {key: items[dep["id"]]["aspect_versions"][key] for key in dep["versions"]}
    a["status"] = "draft"
    return result


def submit_review(data, stage, media_base=None):
    require_valid(data, media_base)
    result = copy.deepcopy(data)
    if stage not in STAGES[:4] or result["pending_review"]:
        raise ValueError("Choose one of four stages; an existing review must be resolved first")
    prior = [a for a in result["artifacts"] if STAGES.index(KIND_STAGE[a["kind"]]) < STAGES.index(stage)]
    if any(a["status"] != "approved" for a in prior):
        raise ValueError("Earlier stages need confirmation")
    targets = [a for a in result["artifacts"] if KIND_STAGE[a["kind"]] == stage and a["status"] != "approved"]
    if not targets or any(a["status"] != "ready" for a in targets):
        raise ValueError("Review needs completed artifacts")
    if stage in ("assets", "storyboard") and media_base is None:
        raise ValueError("Image reviews require local media verification")
    records = []
    for a in targets:
        a["status"] = "awaiting_confirmation"
        records.append(dict(id=a["id"], version=a["version"], digest=digest(a)))
    result["pending_review"] = dict(stage=stage, items=records)
    result["stage"] = stage
    return result


def approve_pending_gate(data, evidence, media_base=None):
    require_valid(data, media_base)
    if not isinstance(evidence, str) or not evidence.strip() or not data.get("pending_review"):
        raise ValueError("An explicit user confirmation of the pending results is required")
    result = copy.deepcopy(data)
    pending = result["pending_review"]
    if pending["stage"] in ("assets", "storyboard") and media_base is None:
        raise ValueError("Image approval requires actual local files")
    items = index(result)
    records = []
    for r in pending["items"]:
        a = items[r["id"]]
        a["status"], a["approved_version"] = "approved", a["version"]
        records.append(dict(r, aspects=copy.deepcopy(a["aspect_versions"])))
    result["approvals"].append(dict(stage=pending["stage"], source="user", evidence=evidence,
                                    at=now(), items=records))
    result["stage"] = STAGES[STAGES.index(pending["stage"]) + 1]
    result["pending_review"] = None
    return result
