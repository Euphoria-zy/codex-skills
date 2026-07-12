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
            errors.append("source `{}` must be an object".format(source_name))
            continue
        source_type = source_value.get("type")
        if source_type not in {"local", "git"}:
            errors.append(
                "source `{}` has unsupported type `{}`".format(
                    source_name, source_type
                )
            )
            continue
        if source_type == "git":
            url = source_value.get("url")
            commit = source_value.get("commit")
            license_name = source_value.get("license")
            license_path = source_value.get("licensePath")
            if not isinstance(url, str) or not url:
                errors.append("source `{}` git URL is missing".format(source_name))
            if not isinstance(commit, str) or not GIT_COMMIT_PATTERN.fullmatch(commit):
                errors.append(
                    "source `{}` commit must be 40 lowercase hexadecimal characters".format(
                        source_name
                    )
                )
            if not isinstance(license_name, str) or not license_name:
                errors.append("source `{}` license is missing".format(source_name))
            if not isinstance(license_path, str) or not _is_relative_path(license_path):
                errors.append("source `{}` licensePath is invalid".format(source_name))
            elif source_name in source_roots:
                if not (source_roots[source_name] / license_path).is_file():
                    errors.append(
                        "source `{}` license file `{}` is missing".format(
                            source_name, license_path
                        )
                    )

    skills_value = lock.get("skills")
    if not isinstance(skills_value, list):
        errors.append("dependency lock skills must be an array")
        skills_value = []

    seen: Set[str] = set()
    for index, skill_value in enumerate(skills_value):
        if not isinstance(skill_value, dict):
            errors.append("skill entry {} must be an object".format(index))
            continue
        name = skill_value.get("name")
        source = skill_value.get("source")
        path_value = skill_value.get("path")

        if not isinstance(name, str) or not name:
            errors.append("skill entry {} has an invalid name".format(index))
            display_name = "#{}".format(index)
        else:
            display_name = name
            if name in seen:
                errors.append("duplicate skill name `{}`".format(name))
            seen.add(name)

        if not isinstance(source, str) or source not in sources:
            errors.append(
                "skill `{}` uses unknown source `{}`".format(display_name, source)
            )
            continue
        if not isinstance(path_value, str) or not _is_relative_path(path_value):
            errors.append("skill `{}` has an invalid path".format(display_name))
            continue

        source_root = source_roots.get(source)
        if source_root is not None:
            skill_root = source_root / path_value
            if not skill_root.is_dir():
                errors.append("skill `{}` directory is missing".format(display_name))
            elif not (skill_root / "SKILL.md").is_file():
                errors.append("skill `{}` is missing `SKILL.md`".format(display_name))

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
                errors.append(
                    "skill `{}` references undeclared dependency `{}`".format(
                        name, reference
                    )
                )
    return errors


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
        print("failed to load dependency lock: {}".format(exc), file=sys.stderr)
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
