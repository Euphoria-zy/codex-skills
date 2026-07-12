"""Build the VibeCoding Guidance plugin from its pinned dependency lock."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Set

from check_plugin_dependencies import (
    load_lock,
    scan_references,
    validate_lock,
    validate_staged_skills,
)


def _run_git(arguments: List[str], cwd: Optional[Path] = None) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=str(cwd) if cwd is not None else None,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def fetch_git_source(url: str, commit: str, destination: Path) -> None:
    """Fetch and check out exactly one locked Git commit."""

    _run_git(["clone", "--no-checkout", url, str(destination)])
    _run_git(["fetch", "--depth", "1", "origin", commit], destination)
    _run_git(["checkout", "--detach", commit], destination)
    actual = _run_git(["rev-parse", "HEAD"], destination)
    if actual != commit:
        raise ValueError(f"fetched commit `{actual}` does not match lock `{commit}`")


def copy_skill(
    source: Path, destination: Path, namespace: str, entry_skill: bool
) -> None:
    """Copy a complete skill and rewrite only generated SKILL.md files."""

    shutil.copytree(str(source), str(destination))
    for manifest in destination.rglob("SKILL.md"):
        text = manifest.read_text(encoding="utf-8")
        text = text.replace("superpowers:", namespace + ":")
        if entry_skill:
            text = re.sub(
                r"(?<![:\w-])coding-standards(?![\w-])",
                namespace + ":coding-standards",
                text,
            )
        manifest.write_text(text, encoding="utf-8")


def create_notice(
    source_root: Path, source: Mapping[str, object], destination: Path
) -> None:
    """Append one locked Git source and its complete license to the notice."""

    license_path = source.get("licensePath")
    if not isinstance(license_path, str):
        raise ValueError("Git source licensePath is invalid")
    license_text = (source_root / license_path).read_text(encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    prefix = "# Third-Party Notices\n\n" if not destination.exists() else ""
    url = source.get("url")
    commit = source.get("commit")
    license_name = source.get("license")
    section = (
        f"## {url}\n\n"
        f"- Source: {url}\n"
        f"- Commit: `{commit}`\n"
        f"- License: {license_name}\n\n"
        f"```text\n{license_text.rstrip()}\n```\n\n"
    )
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(prefix + section)


def _validate_source_closure(
    lock: Mapping[str, object], source_roots: Mapping[str, Path]
) -> List[str]:
    skills = lock.get("skills")
    if not isinstance(skills, list):
        return []
    declared: Set[str] = {
        item["name"]
        for item in skills
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    errors: List[str] = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        source_name = item.get("source")
        relative_path = item.get("path")
        if not all(isinstance(value, str) for value in (name, source_name, relative_path)):
            continue
        source_root = source_roots.get(source_name)
        if source_root is None:
            continue
        for reference in sorted(scan_references(source_root / relative_path)):
            if reference not in declared:
                errors.append(f"skill `{name}` references undeclared dependency `{reference}`")
    return sorted(set(errors))


def build_skills(repo_root: Path, lock_path: Path, destination: Path) -> None:
    """Materialize and validate a complete skills tree at an explicit path."""

    repo_root = repo_root.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"build destination already exists: {destination}")

    lock = load_lock(lock_path)
    sources = lock.get("sources")
    skills = lock.get("skills")
    namespace = lock.get("namespace")
    if not isinstance(sources, dict) or not isinstance(skills, list) or not isinstance(namespace, str):
        raise ValueError("dependency lock has invalid top-level fields")

    created_destination = False
    try:
        with tempfile.TemporaryDirectory(prefix="vibecoding-sources-") as temporary:
            temporary_root = Path(temporary)
            source_roots: Dict[str, Path] = {"repository": repo_root}
            for source_name, source in sources.items():
                if not isinstance(source, dict) or source.get("type") != "git":
                    continue
                url = source.get("url")
                commit = source.get("commit")
                if not isinstance(url, str) or not isinstance(commit, str):
                    raise ValueError(f"Git source `{source_name}` is invalid")
                source_root = temporary_root / source_name
                fetch_git_source(url, commit, source_root)
                source_roots[source_name] = source_root

            errors = validate_lock(lock, source_roots)
            errors.extend(_validate_source_closure(lock, source_roots))
            if errors:
                raise ValueError("\n".join(sorted(set(errors))))

            destination.mkdir(parents=True)
            created_destination = True
            for skill in skills:
                if not isinstance(skill, dict):
                    continue
                name = skill["name"]
                source_name = skill["source"]
                relative_path = skill["path"]
                copy_skill(
                    source_roots[source_name] / relative_path,
                    destination / name,
                    namespace,
                    name == namespace,
                )

            notice_path = destination / ".third-party" / "THIRD_PARTY_NOTICES.md"
            for source_name, source in sources.items():
                if isinstance(source, dict) and source.get("type") == "git":
                    create_notice(source_roots[source_name], source, notice_path)

            staged_errors = validate_staged_skills(destination, lock)
            if staged_errors:
                raise ValueError("\n".join(staged_errors))
    except Exception:
        if created_destination and destination.exists():
            shutil.rmtree(str(destination))
        raise


def install_skills(staged_skills: Path, canonical_skills: Path) -> None:
    """Atomically install staged skills and restore the previous tree on failure."""

    canonical_skills.parent.mkdir(parents=True, exist_ok=True)
    backup = canonical_skills.with_name(
        canonical_skills.name + ".backup-" + uuid.uuid4().hex
    )
    had_existing = canonical_skills.exists()
    if had_existing:
        canonical_skills.replace(backup)
    try:
        staged_skills.replace(canonical_skills)
    except Exception:
        if had_existing and backup.exists():
            backup.replace(canonical_skills)
        raise
    if backup.exists():
        shutil.rmtree(str(backup))


def _trees_match(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False
    left_files = {path.relative_to(left) for path in left.rglob("*") if path.is_file()}
    right_files = {path.relative_to(right) for path in right.rglob("*") if path.is_file()}
    return left_files == right_files and all(
        _files_match(left / relative, right / relative) for relative in left_files
    )


def _files_match(left: Path, right: Path) -> bool:
    left_bytes = left.read_bytes()
    right_bytes = right.read_bytes()
    if left_bytes == right_bytes:
        return True
    try:
        left_text = left_bytes.decode("utf-8")
        right_text = right_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return left_text.replace("\r\n", "\n") == right_text.replace("\r\n", "\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--output", type=Path)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--install", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    plugin_root = repo_root / "plugins" / "vibecoding-guidance"
    lock_path = plugin_root / "dependency-lock.json"
    canonical = plugin_root / "skills"
    try:
        if args.output is not None:
            build_skills(repo_root, lock_path, args.output)
            return 0
        with tempfile.TemporaryDirectory(prefix="vibecoding-build-") as temporary:
            staged = Path(temporary) / "skills"
            build_skills(repo_root, lock_path, staged)
            if args.check:
                if not _trees_match(staged, canonical):
                    print("generated plugin skills differ from a clean rebuild", file=sys.stderr)
                    return 1
                return 0
            install_skills(staged, canonical)
            return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
