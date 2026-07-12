# VibeCoding Guidance Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish one installable `vibecoding-guidance` Codex plugin containing the two repository skills and a pinned, validated Superpowers dependency closure.

**Architecture:** A repo marketplace points to `plugins/vibecoding-guidance`. A JSON dependency lock declares local and pinned Git skill sources. A dependency checker validates closure, namespaces, notices, manifest metadata, generated drift, and version changes; a deterministic builder materializes the standard plugin `skills/` directory from that lock.

**Tech Stack:** Python 3.11 standard library, `unittest`, Git, JSON, GitHub Actions, Codex plugin-creator validation tools.

---

## File map

- Create `.agents/plugins/marketplace.json`: repository marketplace containing the plugin entry.
- Create `.github/workflows/validate-plugin.yml`: CI tests, dependency checks, clean rebuild comparison, and pinned Gitleaks scan.
- Create `AGENTS.md`: repository rules for dependency changes, generated files, version bumps, and release validation.
- Modify `README.md`: replace standalone installation as the primary path with marketplace/plugin installation and upgrade instructions.
- Create `plugins/vibecoding-guidance/.codex-plugin/plugin.json`: canonical plugin manifest.
- Create `plugins/vibecoding-guidance/dependency-lock.json`: authoritative local and pinned Git dependency graph.
- Generate `plugins/vibecoding-guidance/skills/`: bundled skills plus `skills/.third-party/THIRD_PARTY_NOTICES.md`; never edit generated files directly.
- Create `scripts/check_plugin_dependencies.py`: validate lock structure, dependency closure, generated output, manifest/marketplace consistency, and version baselines.
- Create `scripts/build_plugin.py`: fetch locked sources, copy declared skills, rewrite namespaces, generate notices, and swap the bundle safely.
- Create `tests/test_plugin_dependencies.py`: behavior tests for both scripts.

## Task 1: Scaffold the plugin, marketplace, and dependency lock

**Files:**
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/vibecoding-guidance/.codex-plugin/plugin.json`
- Create: `plugins/vibecoding-guidance/dependency-lock.json`

- [ ] **Step 1: Confirm the repository starts clean**

Run:

```powershell
git status --short
```

Expected: no output.

- [ ] **Step 2: Scaffold the repo marketplace and plugin manifest**

Run from the repository root:

```powershell
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/create_basic_plugin.py `
  vibecoding-guidance `
  --path plugins `
  --marketplace-path .agents/plugins/marketplace.json `
  --marketplace-name euphoria-zy-codex-skills `
  --with-marketplace
```

Expected: the plugin folder, `.codex-plugin/plugin.json`, and repo marketplace are created without placeholders.

- [ ] **Step 3: Replace the scaffold manifest with the approved metadata**

Set `plugins/vibecoding-guidance/.codex-plugin/plugin.json` to:

```json
{
  "name": "vibecoding-guidance",
  "version": "0.0.0",
  "description": "Approved, traceable, and verified software delivery with bundled planning, TDD, debugging, and review workflows.",
  "author": {
    "name": "Euphoria-zy",
    "url": "https://github.com/Euphoria-zy"
  },
  "homepage": "https://github.com/Euphoria-zy/codex-skills",
  "repository": "https://github.com/Euphoria-zy/codex-skills",
  "license": "MIT",
  "keywords": ["vibecoding", "planning", "tdd", "debugging", "delivery"],
  "skills": "./skills/",
  "interface": {
    "displayName": "VibeCoding Guidance",
    "shortDescription": "Plan, implement, and verify software through explicit delivery gates",
    "longDescription": "Turn product intent into approved design, traceable implementation, test-driven changes, systematic debugging, and verified delivery.",
    "developerName": "Euphoria-zy",
    "category": "Developer Tools",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Use VibeCoding Guidance to turn this idea into approved, tracked, and verified delivery."
    ]
  }
}
```

- [ ] **Step 4: Set the repo marketplace entry**

Ensure `.agents/plugins/marketplace.json` contains exactly one ordered plugin entry with:

```json
{
  "name": "euphoria-zy-codex-skills",
  "interface": {
    "displayName": "Euphoria-zy Codex Skills"
  },
  "plugins": [
    {
      "name": "vibecoding-guidance",
      "source": {
        "source": "local",
        "path": "./plugins/vibecoding-guidance"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

- [ ] **Step 5: Add the immutable dependency lock**

Create `plugins/vibecoding-guidance/dependency-lock.json` with schema version `1`, namespace `vibecoding-guidance`, and these sources:

```json
{
  "schemaVersion": 1,
  "namespace": "vibecoding-guidance",
  "sources": {
    "repository": {
      "type": "local"
    },
    "superpowers": {
      "type": "git",
      "url": "https://github.com/obra/superpowers.git",
      "commit": "d884ae04edebef577e82ff7c4e143debd0bbec99",
      "license": "MIT",
      "licensePath": "LICENSE"
    }
  },
  "skills": [
    {"name": "vibecoding-guidance", "source": "repository", "path": "skills/vibecoding-guidance"},
    {"name": "coding-standards", "source": "repository", "path": "skills/coding-standards"},
    {"name": "brainstorming", "source": "superpowers", "path": "skills/brainstorming"},
    {"name": "writing-plans", "source": "superpowers", "path": "skills/writing-plans"},
    {"name": "test-driven-development", "source": "superpowers", "path": "skills/test-driven-development"},
    {"name": "systematic-debugging", "source": "superpowers", "path": "skills/systematic-debugging"},
    {"name": "verification-before-completion", "source": "superpowers", "path": "skills/verification-before-completion"},
    {"name": "using-git-worktrees", "source": "superpowers", "path": "skills/using-git-worktrees"},
    {"name": "subagent-driven-development", "source": "superpowers", "path": "skills/subagent-driven-development"},
    {"name": "executing-plans", "source": "superpowers", "path": "skills/executing-plans"},
    {"name": "finishing-a-development-branch", "source": "superpowers", "path": "skills/finishing-a-development-branch"},
    {"name": "requesting-code-review", "source": "superpowers", "path": "skills/requesting-code-review"}
  ],
  "namespaceRewrites": {
    "superpowers:": "vibecoding-guidance:"
  }
}
```

- [ ] **Step 6: Validate configuration syntax and scaffold output**

Run:

```powershell
python -m json.tool .agents/plugins/marketplace.json > $null
python -m json.tool plugins/vibecoding-guidance/.codex-plugin/plugin.json > $null
python -m json.tool plugins/vibecoding-guidance/dependency-lock.json > $null
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
```

Expected: all JSON commands and plugin validation exit `0`. Version `0.0.0` is a valid unreleased scaffold version; Task 4 changes it to the initial release version `0.1.0` before generated output is committed.

- [ ] **Step 7: Commit the scaffold and lock**

```powershell
git add .agents/plugins/marketplace.json plugins/vibecoding-guidance/.codex-plugin/plugin.json plugins/vibecoding-guidance/dependency-lock.json
git commit -m "feat: scaffold vibecoding guidance plugin"
```

## Task 2: Implement dependency discovery and lock validation with TDD

**Files:**
- Create: `tests/test_plugin_dependencies.py`
- Create: `scripts/check_plugin_dependencies.py`

- [ ] **Step 1: Write failing tests for declared and transitive dependencies**

Add `unittest` cases that create temporary skill directories and assert:

```python
def test_finds_namespaced_skill_references(self):
    skill = self.write_skill("entry", "Use `superpowers:brainstorming` and superpowers:writing-plans.")
    self.assertEqual(scan_references(skill), {"brainstorming", "writing-plans"})

def test_reports_undeclared_transitive_dependency(self):
    self.write_skill("entry", "Use superpowers:brainstorming.")
    self.write_skill("brainstorming", "Use superpowers:writing-plans.")
    errors = validate_closure({"entry", "brainstorming"}, self.skills_root)
    self.assertIn("writing-plans", "\n".join(errors))
```

Also add tests for duplicate names, an unknown source, a missing `SKILL.md`, and a missing `licensePath`.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m unittest tests.test_plugin_dependencies -v
```

Expected: import or missing-function failures because `scripts/check_plugin_dependencies.py` does not exist.

- [ ] **Step 3: Implement the minimal lock and closure checker**

Create `scripts/check_plugin_dependencies.py` with these public functions:

```python
def load_lock(path: Path) -> dict[str, object]: ...
def scan_references(skill_dir: Path) -> set[str]: ...
def validate_lock(lock: dict[str, object], source_roots: dict[str, Path]) -> list[str]: ...
def validate_closure(declared: set[str], skills_root: Path) -> list[str]: ...
```

Use only the Python standard library. Match explicit references with `r"superpowers:([a-z0-9-]+)"`. Return deterministic, sorted error messages; do not silently normalize invalid input.

- [ ] **Step 4: Run the focused tests and verify GREEN**

```powershell
python -m unittest tests.test_plugin_dependencies -v
```

Expected: all dependency discovery and lock validation tests pass.

- [ ] **Step 5: Add the repository CLI boundary**

The checker CLI must accept:

```text
python scripts/check_plugin_dependencies.py --repo-root . [--base-ref REV]
```

It loads the canonical lock, resolves local sources, and returns exit `1` with one error per line when validation fails. External Git resolution is deferred to the builder; the checker validates fetched/generated content when the bundle exists.

- [ ] **Step 6: Run all tests and commit**

```powershell
python -m unittest discover -s tests -v
git add tests/test_plugin_dependencies.py scripts/check_plugin_dependencies.py
git commit -m "test: enforce plugin dependency closure"
```

## Task 3: Implement deterministic bundle generation with TDD

**Files:**
- Modify: `tests/test_plugin_dependencies.py`
- Modify: `scripts/check_plugin_dependencies.py`
- Create: `scripts/build_plugin.py`

- [ ] **Step 1: Write failing builder tests**

Add tests proving that a local fixture build:

- copies complete skill directories and supporting files;
- rewrites `superpowers:` to `vibecoding-guidance:` only in generated `SKILL.md` files;
- rewrites the entry skill's explicit `coding-standards` requirement;
- generates the upstream copyright, commit, source URL, and full license in `skills/.third-party/THIRD_PARTY_NOTICES.md`;
- rejects a staged tree with a missing declared skill, an undeclared skill, an unresolved `superpowers:` reference, or an invalid notice before any swap;
- leaves an existing canonical `skills/` directory unchanged when validation fails;
- restores an existing `skills/` directory when the final staged rename is forced to fail;
- can build to an explicit output path without mutating the canonical plugin.

Use a temporary local Git repository as the external source fixture so unit tests do not require network access.

- [ ] **Step 2: Run the builder tests and verify RED**

```powershell
python -m unittest tests.test_plugin_dependencies.PluginBuilderTests -v
```

Expected: import or missing-function failures because `scripts/build_plugin.py` does not exist.

- [ ] **Step 3: Implement the minimal builder**

Create `scripts/build_plugin.py` with:

```python
def fetch_git_source(url: str, commit: str, destination: Path) -> None: ...
def copy_skill(source: Path, destination: Path, namespace: str, entry_skill: bool) -> None: ...
def create_notice(source_root: Path, source: dict[str, object], destination: Path) -> None: ...
def build_skills(repo_root: Path, lock_path: Path, destination: Path) -> None: ...
def install_skills(staged_skills: Path, canonical_skills: Path) -> None: ...
```

First add this pure staged-tree validator to `scripts/check_plugin_dependencies.py`, covered by the failing Task 3 tests:

```python
def validate_staged_skills(staged_skills: Path, lock: dict[str, object]) -> list[str]: ...
```

It validates declared directory membership, required `SKILL.md` files, namespace rewrites, and `skills/.third-party/THIRD_PARTY_NOTICES.md`. It does not inspect Git baselines, the marketplace, or the canonical generated tree; those remain Task 4 behavior.

Implementation requirements:

- fetch the exact commit with Git and verify `git rev-parse HEAD` equals the lock;
- build the entire `skills/` tree at a caller-supplied staging or output path;
- copy every declared directory recursively;
- rewrite only generated `SKILL.md` text;
- run lock and closure validation plus `validate_staged_skills` before swapping;
- import pure validation functions from the checker; the checker must not import the builder;
- support mutually exclusive `--output PATH`, `--check`, and `--install` CLI modes;
- make `--output` and `--check` non-mutating for the canonical plugin;
- swap the canonical `skills/` directory with a backup only in `--install` mode and restore on failure;
- clean temporary directories in a `finally` block;
- never fall back to a branch or latest commit.

- [ ] **Step 4: Run focused tests and verify GREEN**

```powershell
python -m unittest tests.test_plugin_dependencies.PluginBuilderTests -v
```

Expected: all builder tests pass.

- [ ] **Step 5: Refactor only proven duplication and rerun the suite**

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass with no warnings or temporary files left in the repository.

- [ ] **Step 6: Commit the builder**

```powershell
git add scripts/build_plugin.py scripts/check_plugin_dependencies.py tests/test_plugin_dependencies.py
git commit -m "feat: build pinned plugin bundle"
```

## Task 4: Enforce generated drift, namespaces, notices, and version baselines

**Files:**
- Modify: `tests/test_plugin_dependencies.py`
- Modify: `scripts/check_plugin_dependencies.py`

- [ ] **Step 1: Write failing validation tests**

Add tests that fail for:

- a generated skill not listed in the lock;
- a declared skill missing from the canonical plugin `skills/` directory;
- an unresolved `superpowers:` reference;
- an incomplete or wrong third-party notice;
- marketplace/plugin name or path mismatch;
- manifest `skills` path mismatch;
- generated skills drift from a supplied fresh staged build;
- changed lock or generated skills with an unchanged baseline version;
- invalid SemVer;
- initial release with version other than `0.1.0`.

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.test_plugin_dependencies.PluginValidationTests -v
```

Expected: failures identify the missing validation behaviors.

- [ ] **Step 3: Implement the minimum validation behavior**

Add explicit functions for:

```python
def validate_generated_skills(repo_root: Path, lock: dict[str, object], candidate: Path | None = None) -> list[str]: ...
def validate_manifest_and_marketplace(repo_root: Path) -> list[str]: ...
def validate_version_change(repo_root: Path, base_ref: str | None) -> list[str]: ...
```

Baseline rules:

- local default: compare working tree with `HEAD`;
- PR CI: caller passes the PR base SHA;
- push CI: caller passes `github.event.before`;
- no baseline manifest: require exactly `0.1.0`;
- changed lock or generated skills: candidate SemVer must be greater than baseline.

- [ ] **Step 4: Run focused and full tests**

```powershell
python -m unittest tests.test_plugin_dependencies.PluginValidationTests -v
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Bump the manifest to the initial release version**

Change `plugins/vibecoding-guidance/.codex-plugin/plugin.json` from `0.0.0` to `0.1.0` before generating or validating the first committed skills tree.

- [ ] **Step 6: Build the real pinned skills tree**

```powershell
python scripts/build_plugin.py --repo-root . --install
```

Expected: `plugins/vibecoding-guidance/skills/` contains 12 declared skills and `.third-party/THIRD_PARTY_NOTICES.md` records Superpowers commit `d884ae04edebef577e82ff7c4e143debd0bbec99`.

- [ ] **Step 7: Validate the real plugin and generated state without mutation**

```powershell
python scripts/build_plugin.py --repo-root . --check
python scripts/check_plugin_dependencies.py --repo-root .
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
```

Expected: all commands exit `0`; `--check` builds in temporary storage and reports no drift without replacing canonical files.

- [ ] **Step 8: Commit validation, version, and generated skills together**

```powershell
git add scripts/check_plugin_dependencies.py tests/test_plugin_dependencies.py plugins/vibecoding-guidance/.codex-plugin/plugin.json plugins/vibecoding-guidance/skills
git commit -m "feat: validate generated plugin releases"
```

## Task 5: Add repository guidance, CI, installation docs, and publish

**Files:**
- Create: `AGENTS.md`
- Create: `.github/workflows/validate-plugin.yml`
- Modify: `README.md`

- [ ] **Step 1: Add repository guidance**

Create `AGENTS.md` stating:

- edit source skills under root `skills/`, not generated `plugins/vibecoding-guidance/skills/`;
- update `dependency-lock.json` when required skill references change;
- run unit tests, rebuild, run the checker, and validate the plugin;
- bump the plugin version whenever the lock or generated skills change;
- never change the locked Superpowers commit without reviewing and regenerating its notice.

- [ ] **Step 2: Add GitHub Actions validation**

Create `.github/workflows/validate-plugin.yml` that:

- triggers on pull requests and pushes affecting relevant paths;
- checks out full history;
- sets up Python 3.11;
- runs `python -m unittest discover -s tests -v`;
- runs the checker with PR base SHA or push `before` SHA;
- runs `python scripts/build_plugin.py --repo-root . --check` to compare a non-mutating staged build;
- runs `gitleaks/gitleaks-action@dcedce43c6f43de0b836d1fe38946645c9c638dc` with full Git history so the action scans the pull-request or push change range.

- [ ] **Step 3: Update README installation and maintenance instructions**

Document:

```powershell
codex plugin marketplace add Euphoria-zy/codex-skills
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

Also document:

```powershell
codex plugin marketplace upgrade euphoria-zy-codex-skills
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

Keep standalone skill installation as an explicitly labeled development-only option.

- [ ] **Step 4: Run final local verification**

```powershell
python -m unittest discover -s tests -v
python scripts/build_plugin.py --repo-root . --check
python scripts/check_plugin_dependencies.py --repo-root .
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
git diff --check
git status --short
```

Expected: tests and validators pass; rebuild produces no unexpected diff; status lists only the Task 5 files before commit.

- [ ] **Step 5: Commit repository integration**

```powershell
git add AGENTS.md .github/workflows/validate-plugin.yml README.md
git commit -m "docs: publish vibecoding plugin workflow"
```

- [ ] **Step 6: Verify the complete branch and push**

```powershell
python -m unittest discover -s tests -v
python scripts/check_plugin_dependencies.py --repo-root . --base-ref origin/main
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
git log --oneline origin/main..HEAD
git push origin main
git ls-remote origin refs/heads/main
```

Expected: validation passes, all planned commits are visible, push succeeds, and remote `main` resolves to local `HEAD`.

- [ ] **Step 7: Verify remote installation metadata**

Fetch the remote marketplace, manifest, dependency lock, one local bundled skill, one Superpowers bundled skill, and `skills/.third-party/THIRD_PARTY_NOTICES.md`. Confirm each resolves from GitHub `main` and matches the local committed content.
