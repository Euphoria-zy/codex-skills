# VibeCoding Guidance Plugin Design

## Context

The repository currently publishes `vibecoding-guidance` and `coding-standards` as standalone Codex skills. `vibecoding-guidance` requires several Superpowers skills, but installing a standalone skill does not install those dependencies. Codex plugin manifests can bundle skills but do not provide a native skill-to-skill or plugin-to-plugin dependency field.

The plugin must therefore be self-contained at installation time. It will vendor the required Superpowers skill closure from a pinned upstream commit, retain the upstream MIT attribution, and expose the complete workflow as one installable plugin.

## Goals

- Install `vibecoding-guidance`, `coding-standards`, and all required Superpowers skills through one plugin installation.
- Pin third-party sources to immutable Git commits so builds are reproducible.
- Detect undeclared direct or transitive Superpowers skill references before release.
- Keep generated plugin contents synchronized with the dependency lock.
- Publish the plugin and its marketplace entry in `Euphoria-zy/codex-skills`.
- Give future Codex sessions repository guidance for updating dependencies and releasing a new plugin version.

## Non-goals

- Do not install a second plugin at runtime.
- Do not follow the Superpowers `main` branch during user installation.
- Do not silently publish or push dependency upgrades.
- Do not redistribute unrelated Superpowers skills outside the dependency closure.
- Do not change the behavior of the source standalone skills.

## Repository locations

- Remote repository: `https://github.com/Euphoria-zy/codex-skills`
- Current local clone: `C:\Users\29787\Documents\Codex\2026-07-12\new-chat-2\work\codex-skills`
- Plugin directory: `plugins/vibecoding-guidance/`
- Marketplace: `.agents/plugins/marketplace.json`

The generated plugin directory is committed to the same Git repository and pushed to GitHub after validation.

## Plugin structure

```text
codex-skills/
├─ .agents/
│  └─ plugins/
│     └─ marketplace.json
├─ .github/
│  └─ workflows/
│     └─ validate-plugin.yml
├─ docs/
│  └─ superpowers/specs/
│     └─ 2026-07-12-vibecoding-guidance-plugin-design.md
├─ plugins/
│  └─ vibecoding-guidance/
│     ├─ .codex-plugin/
│     │  └─ plugin.json
│     ├─ dependency-lock.json
│     ├─ THIRD_PARTY_NOTICES.md
│     └─ skills/
│        ├─ vibecoding-guidance/
│        ├─ coding-standards/
│        └─ <vendored-superpowers-skills>/
├─ scripts/
│  ├─ build_plugin.py
│  └─ check_plugin_dependencies.py
├─ tests/
│  └─ test_plugin_dependencies.py
├─ AGENTS.md
├─ LICENSE
└─ README.md
```

Only `plugin.json` is stored inside `.codex-plugin/`. Skills and dependency metadata remain at the plugin root, matching Codex plugin path rules.

## Plugin identity

- Plugin name: `vibecoding-guidance`
- Initial plugin version: `0.1.0`
- License: MIT
- Category: Developer Tools
- Skills path: `./skills/`
- Repository: `https://github.com/Euphoria-zy/codex-skills`

The plugin name remains stable across releases. Any change to bundled skill contents or the dependency lock requires a plugin version bump.

## Dependency lock

`plugins/vibecoding-guidance/dependency-lock.json` is the authoritative build input. It records:

- schema version;
- local source skills and paths;
- external source repository, immutable commit, and license;
- each bundled skill name and source path;
- reference namespace mapping used in generated copies.

Conceptual shape:

```json
{
  "schemaVersion": 1,
  "sources": {
    "repository": {
      "type": "local"
    },
    "superpowers": {
      "type": "git",
      "url": "https://github.com/obra/superpowers.git",
      "commit": "d884ae04edebef577e82ff7c4e143debd0bbec99",
      "license": "MIT"
    }
  },
  "skills": [
    {
      "name": "vibecoding-guidance",
      "source": "repository",
      "path": "skills/vibecoding-guidance"
    },
    {
      "name": "coding-standards",
      "source": "repository",
      "path": "skills/coding-standards"
    },
    {
      "name": "brainstorming",
      "source": "superpowers",
      "path": "skills/brainstorming"
    }
  ],
  "namespaceRewrites": {
    "superpowers:": "vibecoding-guidance:"
  }
}
```

The complete initial Superpowers closure is:

- `brainstorming`
- `writing-plans`
- `test-driven-development`
- `systematic-debugging`
- `verification-before-completion`
- `using-git-worktrees`
- `subagent-driven-development`
- `executing-plans`
- `finishing-a-development-branch`
- `requesting-code-review`

This closure is derived from the five direct Superpowers requirements in `vibecoding-guidance` plus transitive `superpowers:<skill>` references.

## Build flow

`scripts/build_plugin.py` performs deterministic generation:

1. Read and validate `dependency-lock.json`.
2. Resolve local skills from the repository.
3. Fetch the external source at the exact locked commit into temporary storage.
4. Copy each declared skill directory, including its supporting files, into the plugin `skills/` directory.
5. Rewrite explicit `superpowers:` references in generated copies to the `vibecoding-guidance:` plugin namespace.
6. Rewrite the generated entry skill's `coding-standards` dependency to the plugin namespace where required.
7. Generate `THIRD_PARTY_NOTICES.md` with the Superpowers source, locked commit, copyright, and full MIT license.
8. Replace the generated skills directory atomically only after all steps succeed.

The standalone source skills remain unchanged. Namespace rewrites occur only in generated plugin copies.

## Dependency checking

`scripts/check_plugin_dependencies.py` validates both source declarations and generated output:

- every explicit `superpowers:<skill>` reference reachable from a declared skill is declared in the lock;
- every declared skill exists at its configured source and path;
- local supporting files remain present after copying;
- generated namespace references do not retain unresolved `superpowers:` requirements;
- no generated skill is present without a lock entry;
- `THIRD_PARTY_NOTICES.md` contains the required upstream copyright and MIT text;
- plugin manifest paths resolve inside the plugin root;
- plugin and marketplace names match;
- the generated tree matches a fresh build from the lock;
- a dependency or bundled-content change is accompanied by a plugin version bump relative to the previous committed manifest.

If a developer adds a new required Superpowers reference without updating the lock, the check fails and reports the missing skill name. The developer must update the lock, rebuild, run tests, and bump the plugin version before release.

## Error handling

- Invalid JSON, unknown schema versions, duplicate skill names, missing paths, or unsupported source types stop before modifying generated output.
- An unavailable Git source or missing locked commit fails the build; it never falls back to `main`.
- Namespace rewrite checks fail on unresolved required Superpowers references.
- A failed build leaves the previously generated plugin intact.
- CI failures block release but do not modify the repository.
- No build or validation script pushes commits automatically.

## Marketplace and installation

`.agents/plugins/marketplace.json` exposes the plugin from the Git subdirectory:

- source type: `git-subdir`;
- repository: `https://github.com/Euphoria-zy/codex-skills.git`;
- path: `./plugins/vibecoding-guidance`;
- ref: `main`;
- installation policy: `AVAILABLE`;
- authentication policy: `ON_INSTALL`.

Users add the repository as a marketplace, refresh it when needed, and install one `vibecoding-guidance` plugin. The installed plugin already contains all locked skills and does not need another dependency installation.

## Release flow

1. Change a source skill or dependency lock.
2. Run dependency tests and observe the expected failure before changing generated output.
3. Rebuild the plugin from the lock.
4. Run the full dependency and plugin validation suite.
5. Increment the plugin version according to the change.
6. Update README release and installation instructions when user-facing behavior changes.
7. Commit the lock, generated plugin, version, notices, tests, and documentation together.
8. Push the validated commit to GitHub.
9. Verify the remote marketplace and manifest resolve to the new commit.

Marketplace refresh or `codex plugin marketplace upgrade` retrieves the new repository snapshot. Automatic silent upgrades are outside this design.

## Repository guidance for future Codex sessions

The root `AGENTS.md` will state that any change to:

- `REQUIRED SUB-SKILL` or `superpowers:<skill>` references;
- `dependency-lock.json`;
- generated plugin skills;
- plugin manifest or marketplace metadata;

must run the dependency checker, rebuild from the lock, bump the plugin version when bundled output changes, and validate before pushing. Generated skill files must not be edited directly.

## CI

`.github/workflows/validate-plugin.yml` runs on pull requests and pushes that affect skills, the plugin, scripts, tests, marketplace metadata, or repository guidance. It performs:

1. unit tests for dependency discovery and failure cases;
2. dependency closure validation;
3. a clean rebuild comparison;
4. plugin manifest and marketplace validation;
5. a secret scan limited to the changed plugin artifacts.

CI reports drift but does not create commits or releases.

## Testing strategy

Implementation follows test-driven development. Tests cover:

- a direct declared dependency;
- recursive transitive dependencies;
- an undeclared dependency failure;
- a missing locked skill failure;
- duplicate dependency rejection;
- immutable commit validation;
- namespace conversion in generated copies;
- unresolved namespace failure;
- third-party notice generation and validation;
- generated-tree drift;
- manifest and marketplace path/name consistency;
- version bump enforcement when bundled output changes.

At least one integration test builds the complete plugin from the pinned Superpowers commit and validates the resulting directory.

## Acceptance criteria

- `plugins/vibecoding-guidance/.codex-plugin/plugin.json` is valid and points to `./skills/`.
- The generated plugin contains both local skills and the complete locked Superpowers closure.
- The plugin contains no unresolved required `superpowers:` references.
- Superpowers copyright and MIT license are included.
- Adding an undeclared dependency causes a clear test or validation failure.
- Rebuilding from the same lock produces the same plugin contents.
- Marketplace metadata resolves to the plugin directory in the GitHub repository.
- README documents marketplace installation and upgrades.
- All tests and validation commands pass before the plugin is pushed.

