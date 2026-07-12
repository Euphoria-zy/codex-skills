# Codex Skills

Reusable Codex skills for minimal, traceable, and verifiable software delivery.

## Included skills

| Skill | Purpose |
| --- | --- |
| [`coding-standards`](skills/coding-standards) | Keep implementation changes minimal, direct, and verifiable. |
| [`vibecoding-guidance`](skills/vibecoding-guidance) | Guide approved, traceable, and verified software delivery from product intent through release. |

## Install with Codex

Invoke `$skill-installer` and ask Codex:

```text
Install these skills from https://github.com/Euphoria-zy/codex-skills:
- skills/coding-standards
- skills/vibecoding-guidance
```

Codex normally detects newly installed skills automatically. Restart Codex if they do not appear.

## Usage

```text
$coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

## Dependencies

`coding-standards` is self-contained.

`vibecoding-guidance` expects these additional skills to be installed:

- `superpowers:brainstorming`
- `superpowers:writing-plans`
- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`
- `superpowers:verification-before-completion`

The repository does not redistribute those third-party skills. Install them from their original source before using the complete `vibecoding-guidance` workflow.

## License

Released under the [MIT License](LICENSE).
