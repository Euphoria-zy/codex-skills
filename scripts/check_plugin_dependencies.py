"""Validate the VibeCoding Guidance plugin dependency lock and skill closure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Set


REFERENCE_PATTERN = re.compile(r"superpowers:([a-z0-9-]+)")
GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")


def load_lock(path: Path) -> Dict[str, object]:
    """Load a dependency lock without altering or normalizing its contents."""

    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("dependency lock must contain a JSON object")
    return value


def scan_references(skill_dir: Path) -> Set[str]:
    """Return explicit Superpowers skill references from one SKILL.md file."""

    manifest = skill_dir / "SKILL.md"
    if not manifest.is_file():
        return set()
    return set(REFERENCE_PATTERN.findall(manifest.read_text(encoding="utf-8")))


def _is_relative_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def validate_lock(
    lock: Mapping[str, object], source_roots: Mapping[str, Path]
) -> List[str]:
    """Validate dependency-lock structure and any available source trees."""

    errors: List[str] = []
    if lock.get("schemaVersion") != 1:
        errors.append("dependency lock schemaVersion must be `1`")

    namespace = lock.get("namespace")
    if not isinstance(namespace, str) or not namespace:
        errors.append("dependency lock namespace must be a non-empty string")

    sources_value = lock.get("sources")
    sources: Mapping[str, object]
    if not isinstance(sources_value, dict):
        errors.append("dependency lock sources must be an object")
        sources = {}
    else:
        sources = sources_value

    for source_name, source_value in sources.items():
        if not isinstance(source_value, dict):
            errors.append(f"source `{source_name}` must be an object")
            continue
        source_type = source_value.get("type")
        if source_type not in {"local", "git"}:
            errors.append(f"source `{source_name}` has unsupported type `{source_type}`")
            continue
        if source_type == "git":
            url = source_value.get("url")
            commit = source_value.get("commit")
            license_name = source_value.get("license")
            license_path = source_value.get("licensePath")
            if not isinstance(url, str) or not url:
                errors.append(f"source `{source_name}` git URL is missing")
            if not isinstance(commit, str) or not GIT_COMMIT_PATTERN.fullmatch(commit):
                errors.append(f"source `{source_name}` commit must be 40 lowercase hexadecimal characters")
            if not isinstance(license_name, str) or not license_name:
                errors.append(f"source `{source_name}` license is missing")
            if not isinstance(license_path, str) or not _is_relative_path(license_path):
                errors.append(f"source `{source_name}` licensePath is invalid")
            elif source_name in source_roots:
                if not (source_roots[source_name] / license_path).is_file():
                    errors.append(f"source `{source_name}` license file `{license_path}` is missing")

    skills_value = lock.get("skills")
    if not isinstance(skills_value, list):
        errors.append("dependency lock skills must be an array")
        skills_value = []

    seen: Set[str] = set()
    for index, skill_value in enumerate(skills_value):
        if not isinstance(skill_value, dict):
            errors.append(f"skill entry {index} must be an object")
            continue
        name = skill_value.get("name")
        source = skill_value.get("source")
        path_value = skill_value.get("path")

        if not isinstance(name, str) or not name:
            errors.append(f"skill entry {index} has an invalid name")
            display_name = f"#{index}"
        else:
            display_name = name
            if name in seen:
                errors.append(f"duplicate skill name `{name}`")
            seen.add(name)

        if not isinstance(source, str) or source not in sources:
            errors.append(f"skill `{display_name}` uses unknown source `{source}`")
            continue
        if not isinstance(path_value, str) or not _is_relative_path(path_value):
            errors.append(f"skill `{display_name}` has an invalid path")
            continue

        source_root = source_roots.get(source)
        if source_root is not None:
            skill_root = source_root / path_value
            if not skill_root.is_dir():
                errors.append(f"skill `{display_name}` directory is missing")
            elif not (skill_root / "SKILL.md").is_file():
                errors.append(f"skill `{display_name}` is missing `SKILL.md`")

    rewrites = lock.get("namespaceRewrites")
    if not isinstance(rewrites, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in rewrites.items()
    ):
        errors.append("dependency lock namespaceRewrites must map strings to strings")

    return sorted(set(errors))


def validate_closure(declared: Set[str], skills_root: Path) -> List[str]:
    """Report referenced skills that are absent from the declared closure."""

    errors: List[str] = []
    for name in sorted(declared):
        skill_dir = skills_root / name
        for reference in sorted(scan_references(skill_dir)):
            if reference not in declared:
                errors.append(f"skill `{name}` references undeclared dependency `{reference}`")
    return errors


def validate_staged_skills(
    staged_skills: Path, lock: Mapping[str, object]
) -> List[str]:
    """Validate a fully materialized skills tree before it is installed."""

    errors: List[str] = []
    skills_value = lock.get("skills")
    sources_value = lock.get("sources")
    namespace = lock.get("namespace")
    if not isinstance(skills_value, list) or not isinstance(sources_value, dict):
        return ["cannot validate staged skills from an invalid dependency lock"]

    declared = {
        item["name"]
        for item in skills_value
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    actual = {
        item.name
        for item in staged_skills.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    } if staged_skills.is_dir() else set()

    for name in sorted(declared - actual):
        errors.append(f"staged skill `{name}` is missing")
    for name in sorted(actual - declared):
        errors.append(f"staged skill `{name}` is not declared in the dependency lock")

    namespaced_pattern = None
    if isinstance(namespace, str) and namespace:
        namespaced_pattern = re.compile(
            re.escape(namespace) + r":([a-z0-9-]+)"
        )
    for name in sorted(actual & declared):
        manifest = staged_skills / name / "SKILL.md"
        if not manifest.is_file():
            errors.append(f"staged skill `{name}` is missing `SKILL.md`")
            continue
        for skill_manifest in sorted((staged_skills / name).rglob("SKILL.md")):
            text = skill_manifest.read_text(encoding="utf-8")
            if "superpowers:" in text:
                errors.append(f"staged skill `{name}` contains unresolved `superpowers:` references")
            if namespaced_pattern is not None:
                for reference in namespaced_pattern.findall(text):
                    if reference not in declared:
                        errors.append(f"staged skill `{name}` references undeclared dependency `{reference}`")

    git_sources = [
        (name, value)
        for name, value in sources_value.items()
        if isinstance(value, dict) and value.get("type") == "git"
    ]
    if git_sources:
        notice_path = staged_skills / ".third-party" / "THIRD_PARTY_NOTICES.md"
        if not notice_path.is_file():
            errors.append("third-party notice is missing")
        else:
            notice = notice_path.read_text(encoding="utf-8")
            for source_name, source in git_sources:
                for field in ("url", "commit", "license"):
                    value = source.get(field)
                    if isinstance(value, str) and value not in notice:
                        errors.append(f"third-party notice is missing {field} for source `{source_name}`")

    return sorted(set(errors))


def _declared_skills(lock: Mapping[str, object]) -> Set[str]:
    skills = lock.get("skills")
    if not isinstance(skills, list):
        return set()
    return {
        item["name"]
        for item in skills
        if isinstance(item, dict)
        and isinstance(item.get("name"), str)
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--base-ref",
        help="Git baseline used by release validation (accepted for forward compatibility).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    lock_path = repo_root / "plugins" / "vibecoding-guidance" / "dependency-lock.json"
    try:
        lock = load_lock(lock_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"failed to load dependency lock: {exc}", file=sys.stderr)
        return 1

    errors = validate_lock(lock, {"repository": repo_root})
    errors.extend(
        validate_closure(_declared_skills(lock), repo_root / "skills")
    )
    for error in sorted(set(errors)):
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
