# Codex Skills

Reusable Codex skills for minimal, traceable, and verifiable software delivery.

## Installation options

Installing standalone skills is the simplest way to write, inspect, and use Codex skills, so it is the recommended default. The plugin does not replace the skill format; it packages `vibecoding-guidance`, `coding-standards`, and the required Superpowers skill dependencies into one installable bundle.

| Method | Recommended for | Dependency behavior |
| --- | --- | --- |
| Standalone skills **(recommended)** | Simple installation, direct skill development, or using only the skills you need | Installs only the selected repository skills |
| Plugin | Using the complete `vibecoding-guidance` workflow without installing every dependency separately | Installs the repository skills and pinned Superpowers dependency closure together |

### Install standalone skills (recommended)

The current Codex CLI does not expose a `codex skill add` subcommand. Use the built-in `$skill-installer` through Codex and include the repository address:

```powershell
codex 'Use $skill-installer to install skills/coding-standards and skills/vibecoding-guidance from https://github.com/Euphoria-zy/codex-skills'
```

To install only the self-contained `coding-standards` skill:

```powershell
codex 'Use $skill-installer to install skills/coding-standards from https://github.com/Euphoria-zy/codex-skills'
```

Standalone skills use their short names:

```text
$coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

`coding-standards` is self-contained. A standalone `vibecoding-guidance` installation does not automatically install its Superpowers dependencies. Install those dependencies separately or use the plugin for the complete workflow.

### Install the plugin (dependency bundle)

Add this GitHub repository as a Codex plugin marketplace, then install the bundled plugin:

```powershell
codex plugin marketplace add Euphoria-zy/codex-skills --ref main
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

Plugin skills use the marketplace namespace:

```text
$vibecoding-guidance:coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance:vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

To update an existing plugin installation:

```powershell
codex plugin marketplace upgrade euphoria-zy-codex-skills
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

Start a new Codex task after either installation method so the newly installed skills are loaded.

## Included source skills

| Skill | Purpose |
| --- | --- |
| [`coding-standards`](skills/coding-standards) | Keep implementation changes minimal, direct, and verifiable. |
| [`vibecoding-guidance`](skills/vibecoding-guidance) | Guide approved, traceable, and verified software delivery from product intent through release. |

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
