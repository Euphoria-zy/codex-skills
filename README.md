# Codex Skills

Reusable Codex skills for minimal, traceable, and verifiable software delivery.

## One-click plugin installation

Add this repository as a Codex plugin marketplace, then install the plugin:

```powershell
codex plugin marketplace add Euphoria-zy/codex-skills --ref main
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

The plugin installs `vibecoding-guidance`, `coding-standards`, and the complete pinned Superpowers dependency set together. No separate dependency installation is required.

Start a new Codex task after installation so the plugin skills are loaded.

To update an existing installation:

```powershell
codex plugin marketplace upgrade euphoria-zy-codex-skills
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

## Included source skills

| Skill | Purpose |
| --- | --- |
| [`coding-standards`](skills/coding-standards) | Keep implementation changes minimal, direct, and verifiable. |
| [`vibecoding-guidance`](skills/vibecoding-guidance) | Guide approved, traceable, and verified software delivery from product intent through release. |

## Development-only standalone installation

Standalone installation is useful only while editing the two repository source skills. It does not install the bundled dependency closure. Invoke `$skill-installer` and ask Codex:

```text
Install these skills from https://github.com/Euphoria-zy/codex-skills:
- skills/coding-standards
- skills/vibecoding-guidance
```

Codex normally detects newly installed skills automatically. Restart Codex if they do not appear.

## Plugin usage

Use the namespaced skill names in a new Codex task:

```text
$vibecoding-guidance:coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance:vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

If the standalone source skills are also installed locally, their shorter names remain available separately:

```text
$coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

## Bundled dependencies

`coding-standards` is self-contained.

The plugin redistributes these pinned Superpowers skills under their MIT license:

- `superpowers:brainstorming`
- `superpowers:writing-plans`
- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`
- `superpowers:verification-before-completion`
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:executing-plans`
- `superpowers:finishing-a-development-branch`
- `superpowers:requesting-code-review`

Inside the plugin, their references are rewritten to the `vibecoding-guidance:` namespace. The exact upstream repository and commit are recorded in [`dependency-lock.json`](plugins/vibecoding-guidance/dependency-lock.json), and the complete upstream license is preserved in [`THIRD_PARTY_NOTICES.md`](plugins/vibecoding-guidance/skills/.third-party/THIRD_PARTY_NOTICES.md).

## Plugin maintenance

After changing a source skill or dependency lock:

```powershell
python -m unittest discover -s tests -v
python scripts/build_plugin.py --repo-root . --install
python scripts/build_plugin.py --repo-root . --check
python scripts/check_plugin_dependencies.py --repo-root .
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
```

Generated files under `plugins/vibecoding-guidance/skills/` must not be edited directly. Any lock or generated-content change requires a plugin version bump.

## License

Released under the [MIT License](LICENSE).
