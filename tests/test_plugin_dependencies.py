"""Plugin 依赖锁、构建和发布校验测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_plugin_dependencies import (
    scan_references,
    validate_closure,
    validate_lock,
    validate_staged_skills,
)
from build_plugin import build_skills, install_skills


class PluginDependencyTests(unittest.TestCase):
    """验证 Skill 引用发现和依赖锁的正式契约。"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.skills_root = self.root / "skills"
        self.skills_root.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_skill(self, name: str, body: str, include_manifest: bool = True) -> Path:
        skill_dir = self.skills_root / name
        skill_dir.mkdir(parents=True)
        if include_manifest:
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Use when testing {name}.\n---\n\n{body}\n",
                encoding="utf-8",
            )
        return skill_dir

    def make_lock(self, skills: list[dict[str, str]], sources: dict[str, dict[str, str]] | None = None) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "namespace": "vibecoding-guidance",
            "sources": sources or {"repository": {"type": "local"}},
            "skills": skills,
            "namespaceRewrites": {"superpowers:": "vibecoding-guidance:"},
        }

    def test_finds_namespaced_skill_references(self) -> None:
        skill = self.write_skill("entry", "Use `superpowers:brainstorming` and superpowers:writing-plans.")

        self.assertEqual(scan_references(skill), {"brainstorming", "writing-plans"})

    def test_reports_undeclared_transitive_dependency(self) -> None:
        self.write_skill("entry", "Use superpowers:brainstorming.")
        self.write_skill("brainstorming", "Use superpowers:writing-plans.")

        errors = validate_closure({"entry", "brainstorming"}, self.skills_root)

        self.assertIn("writing-plans", "\n".join(errors))

    def test_rejects_duplicate_skill_names(self) -> None:
        entry = self.write_skill("entry", "No dependencies.")
        lock = self.make_lock(
            [
                {"name": "entry", "source": "repository", "path": str(entry.relative_to(self.root))},
                {"name": "entry", "source": "repository", "path": str(entry.relative_to(self.root))},
            ]
        )

        errors = validate_lock(lock, {"repository": self.root})

        self.assertIn("duplicate skill name `entry`", errors)

    def test_rejects_unknown_skill_source(self) -> None:
        lock = self.make_lock([{"name": "entry", "source": "missing", "path": "skills/entry"}])

        errors = validate_lock(lock, {"repository": self.root})

        self.assertIn("skill `entry` uses unknown source `missing`", errors)

    def test_rejects_missing_skill_manifest(self) -> None:
        entry = self.write_skill("entry", "", include_manifest=False)
        lock = self.make_lock([{"name": "entry", "source": "repository", "path": str(entry.relative_to(self.root))}])

        errors = validate_lock(lock, {"repository": self.root})

        self.assertIn("skill `entry` is missing `SKILL.md`", errors)

    def test_rejects_git_source_without_license_file(self) -> None:
        external_root = self.root / "external"
        external_root.mkdir()
        skill_dir = external_root / "skills" / "entry"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: entry\ndescription: Use when testing.\n---\n", encoding="utf-8")
        sources = {
            "superpowers": {
                "type": "git",
                "url": "https://example.com/superpowers.git",
                "commit": "a" * 40,
                "license": "MIT",
                "licensePath": "LICENSE",
            }
        }
        lock = self.make_lock([{"name": "entry", "source": "superpowers", "path": "skills/entry"}], sources)

        errors = validate_lock(lock, {"superpowers": external_root})

        self.assertIn("source `superpowers` license file `LICENSE` is missing", errors)


class PluginBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repo_root = self.root / "repository"
        self.repo_root.mkdir()
        self.external_root = self.root / "superpowers"
        self.external_root.mkdir()

        self.write_skill(
            self.repo_root,
            "vibecoding-guidance",
            "Use superpowers:brainstorming and coding-standards.",
            {"assets/example.txt": "supporting file"},
        )
        self.write_skill(self.repo_root, "coding-standards", "No dependencies.")
        self.write_skill(
            self.external_root,
            "brainstorming",
            "Use superpowers:writing-plans.",
        )
        self.write_skill(self.external_root, "writing-plans", "No dependencies.")
        (self.external_root / "LICENSE").write_text(
            "Copyright (c) 2024 Fixture Author\n\nMIT fixture license\n",
            encoding="utf-8",
        )
        self.git("init", cwd=self.external_root)
        self.git("config", "user.email", "fixture@example.com", cwd=self.external_root)
        self.git("config", "user.name", "Fixture", cwd=self.external_root)
        self.git("add", ".", cwd=self.external_root)
        self.git("commit", "-m", "fixture", cwd=self.external_root)
        self.commit = self.git("rev-parse", "HEAD", cwd=self.external_root).strip()

        plugin_root = self.repo_root / "plugins" / "vibecoding-guidance"
        plugin_root.mkdir(parents=True)
        self.lock = {
            "schemaVersion": 1,
            "namespace": "vibecoding-guidance",
            "sources": {
                "repository": {"type": "local"},
                "superpowers": {
                    "type": "git",
                    "url": str(self.external_root),
                    "commit": self.commit,
                    "license": "MIT",
                    "licensePath": "LICENSE",
                },
            },
            "skills": [
                {"name": "vibecoding-guidance", "source": "repository", "path": "skills/vibecoding-guidance"},
                {"name": "coding-standards", "source": "repository", "path": "skills/coding-standards"},
                {"name": "brainstorming", "source": "superpowers", "path": "skills/brainstorming"},
                {"name": "writing-plans", "source": "superpowers", "path": "skills/writing-plans"},
            ],
            "namespaceRewrites": {"superpowers:": "vibecoding-guidance:"},
        }
        self.lock_path = plugin_root / "dependency-lock.json"
        import json

        self.lock_path.write_text(json.dumps(self.lock), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def git(self, *args: str, cwd: Path) -> str:
        import subprocess

        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def write_skill(
        self,
        root: Path,
        name: str,
        body: str,
        extra_files: dict[str, str] | None = None,
    ) -> Path:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Fixture skill.\n---\n\n{body}\n",
            encoding="utf-8",
        )
        for relative, content in (extra_files or {}).items():
            destination = skill_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return skill_dir

    def test_build_copies_rewrites_and_generates_notice(self) -> None:
        output = self.root / "output"

        build_skills(self.repo_root, self.lock_path, output)

        entry = (output / "vibecoding-guidance" / "SKILL.md").read_text(encoding="utf-8")
        upstream = (output / "brainstorming" / "SKILL.md").read_text(encoding="utf-8")
        notice = (output / ".third-party" / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertEqual((output / "vibecoding-guidance" / "assets" / "example.txt").read_text(), "supporting file")
        self.assertIn("vibecoding-guidance:brainstorming", entry)
        self.assertIn("vibecoding-guidance:coding-standards", entry)
        self.assertIn("vibecoding-guidance:writing-plans", upstream)
        self.assertNotIn("superpowers:", entry + upstream)
        self.assertIn(self.commit, notice)
        self.assertIn(str(self.external_root), notice)
        self.assertIn("Copyright (c) 2024 Fixture Author", notice)
        self.assertIn("MIT fixture license", notice)

    def test_staged_validation_rejects_missing_and_undeclared_skills(self) -> None:
        output = self.root / "output"
        build_skills(self.repo_root, self.lock_path, output)
        (output / "writing-plans" / "SKILL.md").unlink()
        (output / "extra" ).mkdir()
        (output / "extra" / "SKILL.md").write_text("extra", encoding="utf-8")

        errors = validate_staged_skills(output, self.lock)

        combined = "\n".join(errors)
        self.assertIn("writing-plans", combined)
        self.assertIn("extra", combined)

    def test_staged_validation_rejects_unresolved_namespace_and_notice(self) -> None:
        output = self.root / "output"
        build_skills(self.repo_root, self.lock_path, output)
        manifest = output / "brainstorming" / "SKILL.md"
        manifest.write_text(manifest.read_text(encoding="utf-8") + "\nsuperpowers:missing\n", encoding="utf-8")
        (output / ".third-party" / "THIRD_PARTY_NOTICES.md").write_text("incomplete", encoding="utf-8")

        errors = validate_staged_skills(output, self.lock)

        combined = "\n".join(errors)
        self.assertIn("superpowers:", combined)
        self.assertIn("notice", combined.lower())

    def test_install_restores_existing_skills_when_final_swap_fails(self) -> None:
        staged = self.root / "staged"
        canonical = self.root / "canonical"
        staged.mkdir()
        canonical.mkdir()
        (staged / "new.txt").write_text("new", encoding="utf-8")
        (canonical / "old.txt").write_text("old", encoding="utf-8")

        original_replace = Path.replace
        calls = 0

        def fail_second_replace(path: Path, target: Path) -> Path:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("forced final rename failure")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", fail_second_replace):
            with self.assertRaises(OSError):
                install_skills(staged, canonical)

        self.assertEqual((canonical / "old.txt").read_text(encoding="utf-8"), "old")


if __name__ == "__main__":
    unittest.main()
