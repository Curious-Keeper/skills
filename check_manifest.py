#!/usr/bin/env python3
"""Check that manifest.json stays aligned with the toolchain contracts."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def _toolchain_root() -> Path | None:
    configured = os.environ.get("SPRINT_HARNESS_ROOT")
    if configured:
        root = Path(configured).expanduser()
    else:
        root = ROOT.parent / "sprint-harness"
    return root if root.exists() else None


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AssertionError(f"{path}: cannot read JSON: {exc}") from exc


def _check_shape(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("toolchain", "skills"):
        if not isinstance(manifest.get(key), dict):
            errors.append(f"manifest.{key} must be an object")
    for name, row in manifest.get("skills", {}).items():
        if not isinstance(row, dict):
            errors.append(f"skills.{name} must be an object")
            continue
        allowed = {"readsConfig", "readsMap", "writesMap", "writesFiles"}
        extra = sorted(set(row) - allowed)
        if extra:
            errors.append(f"skills.{name} has unknown keys: {', '.join(extra)}")
        for field in ("readsConfig", "readsMap", "writesMap"):
            value = row.get(field)
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                errors.append(f"skills.{name}.{field} must be a string array")
        if "writesFiles" in row:
            value = row["writesFiles"]
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                errors.append(f"skills.{name}.writesFiles must be a string array")
    return errors


def _readme_coupled_skills() -> set[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    found: set[str] = set()
    for line in readme.splitlines():
        if not line.startswith("|") or "`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        flags = cells[0].replace("`", "")
        match = re.search(r"`([^`]+)`", cells[1])
        if match and "M" in flags:
            found.add(match.group(1))
    return found


def _collect_json_paths(node: Any, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key.startswith("$"):
                continue
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            paths.update(_collect_json_paths(value, path))
    elif isinstance(node, list):
        for item in node:
            paths.update(_collect_json_paths(item, prefix))
    return paths


def _schema_paths(schema: Any, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    if not isinstance(schema, dict):
        return paths
    props = schema.get("properties")
    if isinstance(props, dict):
        for key, value in props.items():
            if key.startswith("$"):
                continue
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            paths.update(_schema_paths(value, path))
    additional = schema.get("additionalProperties")
    if isinstance(additional, dict) and prefix:
        paths.add(f"{prefix}.*")
    items = schema.get("items")
    if isinstance(items, dict):
        paths.update(_schema_paths(items, prefix))
    return paths


def _known(path: str, allowed: set[str]) -> bool:
    if path in allowed:
        return True
    return any(token.endswith(".*") and path.startswith(token[:-1])
               for token in allowed)


def _contract_paths() -> tuple[set[str], set[str], list[str]]:
    errors: list[str] = []
    root = _toolchain_root()
    if root is None:
        return set(), set(), [
            "sprint-harness not found; set SPRINT_HARNESS_ROOT to validate contracts",
        ]

    skeleton = root / "templates" / "MAP.skeleton.json"
    config_schema = root / "harness.config.schema.json"
    map_paths = _collect_json_paths(_load_json(skeleton))
    config_paths = _schema_paths(_load_json(config_schema))
    return map_paths, config_paths, errors


def check() -> list[str]:
    manifest = _load_json(ROOT / "manifest.json")
    errors = _check_shape(manifest)

    listed = set(manifest.get("skills", {}))
    coupled = _readme_coupled_skills()
    for name in sorted(coupled - listed):
        errors.append(f"README marks {name} as harness-coupled, but manifest.json omits it")
    for name in sorted(listed - coupled):
        errors.append(f"manifest.json lists {name}, but README does not mark it with M")

    for name in sorted(listed):
        if not (ROOT / name / "SKILL.md").exists():
            errors.append(f"manifest.json lists {name}, but {name}/SKILL.md does not exist")

    map_paths, config_paths, contract_errors = _contract_paths()
    errors.extend(contract_errors)
    if map_paths:
        for name, row in manifest.get("skills", {}).items():
            for field in ("readsMap", "writesMap"):
                for path in row.get(field, []):
                    if not _known(path, map_paths):
                        errors.append(f"skills.{name}.{field} names unknown map path {path}")
    if config_paths:
        for name, row in manifest.get("skills", {}).items():
            for path in row.get("readsConfig", []):
                if not _known(path, config_paths):
                    errors.append(f"skills.{name}.readsConfig names unknown config path {path}")

    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("manifest contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
