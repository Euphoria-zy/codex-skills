# Repository guidance

- Edit source skills under the repository-level `skills/` directory. Never edit generated files under `plugins/vibecoding-guidance/skills/` directly.
- Update `plugins/vibecoding-guidance/dependency-lock.json` whenever required skill references or upstream sources change.
- Rebuild with `python scripts/build_plugin.py --repo-root . --install` after changing a source skill or dependency lock.
- Bump the plugin SemVer in `plugins/vibecoding-guidance/.codex-plugin/plugin.json` whenever the dependency lock or generated skills change.
- Never change the locked Superpowers commit without reviewing the new upstream content, license, and regenerated third-party notice.
- Before committing, run the unit tests, clean rebuild check, dependency checker, and official plugin validator documented in `README.md`.
