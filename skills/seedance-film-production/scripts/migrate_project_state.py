"""Explicit, lossless 1.x -> 2.0 migration; source and existing targets are never changed."""
import copy
import hashlib
import json
import sys
from pathlib import Path
import legacy_project_state as legacy
from project_state_v2 import new_state, new_artifact, now


def migrate(data, source_path=None):
    if not isinstance(data, dict) or not str(data.get("schema_version", "")).startswith("1."):
        raise ValueError("Migration accepts legacy 1.x only")
    errors, warnings = legacy.validate(data)
    if errors:
        raise ValueError("Legacy validation failed: " + "; ".join(errors))
    result = new_state(data["project_id"], data.get("production_rules", {}).get("default_aspect_ratio", "16:9"))
    result["revision"] = data["revision"]
    result["task_mode"] = data.get("task_mode", "full_production")
    result["source_lock"] = copy.deepcopy(data.get("source_lock", {}))
    result["specialist_tasks"] = copy.deepcopy(data.get("specialist_tasks", []))
    result["legacy_snapshot"] = copy.deepcopy(data)
    result["migration"] = dict(from_schema=data["schema_version"], at=now(), warnings=warnings,
                               source_directory=str(Path(source_path).resolve().parent) if source_path else None,
                               review_policy="reuse_evidence_explicitly_no_new_approval", id_map=[])
    ids = set()
    def add(raw, kind, locator, fallback):
        aid = raw.get("id") or fallback
        if aid in ids:
            raise ValueError(f"Conflicting legacy ID {aid}; resolve explicitly before migration")
        ids.add(aid)
        artifact = new_artifact(aid, kind, {"legacy_data": copy.deepcopy(raw)})
        artifact["version"] = raw.get("version", 1) if isinstance(raw.get("version", 1), int) else 1
        if kind == "board":
            artifact["content"]["style"] = raw.get("style", "legacy_unspecified")
        result["artifacts"].append(artifact)
        result["migration"]["id_map"].append(dict(source=locator, id=aid))
        return aid
    script = data.get("adapted_script", {})
    for i, scene in enumerate(script.get("scenes", [])):
        add(scene, "scene", f"adapted_script.scenes[{i}]", f"LEGACY-SCENE-{i + 1}")
    for i, aid in enumerate(script.get("scene_ids", [])):
        if aid not in ids:
            add({"id": aid, "source": "legacy_snapshot.adapted_script"}, "scene", f"adapted_script.scene_ids[{i}]", aid)
    board_ids = {aid for segment in data.get("segments", []) for aid in segment.get("storyboard_asset_ids", [])}
    for i, asset in enumerate(data.get("assets", [])):
        kind = "board" if asset.get("id") in board_ids or str(asset.get("type", asset.get("kind", ""))).lower() in ("storyboard", "board", "storyboard_16grid") else "asset"
        add(asset, kind, f"assets[{i}]", f"LEGACY-ASSET-{i + 1}")
    for i, segment in enumerate(data.get("segments", [])):
        sid = add(segment, "unit", f"segments[{i}]", f"LEGACY-UNIT-{i + 1}")
        for j, shot in enumerate(segment.get("shots", [])):
            add(shot, "shot", f"segments[{i}].shots[{j}]", f"{sid}-SHOT-{shot.get('number', j + 1)}")
        board = segment.get("storyboard")
        if isinstance(board, dict) and board.get("id") and board["id"] not in ids:
            add(board, "board", f"segments[{i}].storyboard", board["id"])
    for i, prompt in enumerate(data.get("compiled_prompts", [])):
        add(prompt, "prompt", f"compiled_prompts[{i}]", f"LEGACY-PROMPT-{i + 1}")
    return result


def migrate_file(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or destination.exists():
        raise ValueError("Choose a new output file; overwrite is forbidden")
    original = source.read_bytes()
    result = migrate(json.loads(original.decode("utf-8-sig")), source)
    result["migration"]["source_sha256"] = hashlib.sha256(original).hexdigest()
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: migrate_project_state.py OLD.json NEW.json")
    try:
        migrate_file(sys.argv[1], sys.argv[2])
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
    print("Migrated without replacing source, media or historical approval records. Review imported drafts before use.")
