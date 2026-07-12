"""Plugin 依赖锁、构建和发布校验测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_plugin_dependencies import scan_references, validate_closure, validate_lock


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


if __name__ == "__main__":
    unittest.main()
