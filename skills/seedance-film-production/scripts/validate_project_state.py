#!/usr/bin/env python3
"""Validate 1.x unchanged; dispatch Schema 2.0 without implicit migration."""
import json
import sys
from pathlib import Path
from legacy_project_state import GATE_ORDER, count_prompt_characters, load
import legacy_project_state as legacy
import project_state_v2 as v2


def validate(data):
    return v2.validate(data) if isinstance(data, dict) and data.get('schema_version') == '2.0' else legacy.validate(data)


def apply_change(data, *args, **kwargs):
    return (v2 if data.get('schema_version') == '2.0' else legacy).apply_change(data, *args, **kwargs)


def approve_pending_gate(data, *args, **kwargs):
    return (v2 if data.get('schema_version') == '2.0' else legacy).approve_pending_gate(data, *args, **kwargs)


def main():
    if len(sys.argv) != 2:
        print('Usage: validate_project_state.py STATE.json')
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        errors, warnings = validate(data)
        if not errors and data.get('schema_version') == '2.0':
            errors += v2.verify_media(data, path.parent)
    except (ValueError, OSError) as exc:
        print(f'Invalid state: {exc}')
        return 1
    for warning in warnings:
        print(f'Warning: {warning}')
    for error in errors:
        print(f'Error: {error}')
    if not errors:
        print(f"Valid Schema {data.get('schema_version')} state: {path}")
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
