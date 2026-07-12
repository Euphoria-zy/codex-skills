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
│     └─ bundle/                   # Generated and replaced as one unit
│        ├─ THIRD_PARTY_NOTICES.md
│        └─ skills/
│           ├─ vibecoding-guidance/
│           ├─ coding-standards/
│           └─ <vendored-superpowers-skills>/
├─ scripts/
│  ├─ build_plugin.py
│  └─ check_plugin_dependencies.py
├─ tests/
│  └─ test_plugin_dependencies.py
├─ AGENTS.md
├─ LICENSE
└─ README.md
```

Only `plugin.json` is stored inside `.codex-plugin/`. Dependency metadata remains at the plugin root. Generated skills and their third-party notice live together under `bundle/`, allowing the build to replace all generated artifacts as one rollback-safe unit.

## Plugin identity

- Plugin name: `vibecoding-guidance`
- Initial plugin version: `0.1.0`
- License: MIT
- Category: Developer Tools
- Skills path: `./bundle/skills/`
- Repository: `https://github.com/Euphoria-zy/codex-skills`

The plugin name remains stable across releases. Any change to bundled skill contents or the dependency lock requires a plugin version bump.

The initial canonical manifest is:

```json
{
  "name": "vibecoding-guidance",
  "version": "0.1.0",
  "description": "Approved, traceable, and verified software delivery with bundled planning, TDD, debugging, and review workflows.",
  "author": {
    "name": "Euphoria-zy",
    "url": "https://github.com/Euphoria-zy"
  },
  "homepage": "https://github.com/Euphoria-zy/codex-skills",
  "repository": "https://github.com/Euphoria-zy/codex-skills",
  "license": "MIT",
  "keywords": ["vibecoding", "planning", "tdd", "debugging", "delivery"],
  "skills": "./bundle/skills/",
  "interface": {
    "displayName": "VibeCoding Guidance",
    "shortDescription": "Plan, implement, and verify software through explicit delivery gates",
    "longDescription": "Turn product intent into approved design, traceable implementation, test-driven changes, systematic debugging, and verified delivery.",
    "developerName": "Euphoria-zy",
    "category": "Developer Tools",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Use VibeCoding Guidance to turn this product idea into approved, tracked, and verified software delivery."
    ]
  }
}
```

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
      "license": "MIT",
      "licensePath": "LICENSE"
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
4. Copy each declared skill directory, including its supporting files, into a staged `bundle/skills/` directory.
5. Rewrite explicit `superpowers:` references in generated copies to the `vibecoding-guidance:` plugin namespace.
6. Rewrite every explicit `coding-standards` dependency in the generated entry skill to `vibecoding-guidance:coding-standards`.
7. Read the upstream license from the locked source's declared `licensePath` and generate `bundle/THIRD_PARTY_NOTICES.md` with the source, locked commit, copyright, and full MIT license.
8. Build and validate the complete staged `bundle/` directory beside the current bundle on the same volume.
9. Perform a rollback-safe swap of `plugins/vibecoding-guidance/bundle/`: rename the current bundle to a backup, rename the staged bundle into place, then delete the backup. If the second rename fails, restore the backup and fail. On Windows, locked files cause a clear failure rather than partial output.

The standalone source skills remain unchanged. Namespace rewrites occur only in generated plugin copies.

## Dependency checking

`scripts/check_plugin_dependencies.py` validates both source declarations and generated output:

- every explicit `superpowers:<skill>` reference reachable from a declared skill is declared in the lock;
- every declared skill exists at its configured source and path;
- local supporting files remain present after copying;
- generated namespace references do not retain unresolved `superpowers:` requirements;
- no generated skill is present without a lock entry;
- `bundle/THIRD_PARTY_NOTICES.md` contains the required upstream copyright and MIT text;
- plugin manifest paths resolve inside the plugin root;
- plugin and marketplace names match;
- the generated tree matches a fresh build from the lock;
- a dependency or bundled-content change is accompanied by a plugin version bump relative to an explicitly selected Git baseline.

If a developer adds a new required Superpowers reference without updating the lock, the check fails and reports the missing skill name. The developer must update the lock, rebuild, run tests, and bump the plugin version before release.

## Error handling

- Invalid JSON, unknown schema versions, duplicate skill names, missing paths, or unsupported source types stop before modifying generated output.
- An unavailable Git source or missing locked commit fails the build; it never falls back to `main`.
- Namespace rewrite checks fail on unresolved required Superpowers references.
- A failed build before the swap leaves the previous `bundle/` intact. A failed bundle swap restores the backup or reports both the primary and restoration errors without claiming success.
- CI failures block release but do not modify the repository.
- No build or validation script pushes commits automatically.

## Marketplace and installation

After `Euphoria-zy/codex-skills` is added as a marketplace source, `.agents/plugins/marketplace.json` resolves the plugin relative to that marketplace repository root:

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

The marketplace source itself is added from `Euphoria-zy/codex-skills` and may be pinned or refreshed by Codex. The entry inside the marketplace must use the local relative path above; it must not repeat the Git repository as a `git-subdir` source.

Users add the repository as a marketplace, refresh it when needed, and install one `vibecoding-guidance` plugin. The installed plugin already contains all locked skills and does not need another dependency installation.

## Release flow

1. Change a source skill or dependency lock.
2. Run dependency tests and observe the expected failure before changing generated output.
3. Rebuild the plugin from the lock.
4. Increment the plugin version according to the change.
5. Run the full dependency and plugin validation suite against the selected Git baseline.
6. Update README release and installation instructions when user-facing behavior changes.
7. Commit the lock, generated plugin, version, notices, tests, and documentation together.
8. Push the validated commit to GitHub.
9. Verify the remote marketplace and manifest resolve to the new commit.

Marketplace refresh or `codex plugin marketplace upgrade` retrieves the new repository snapshot. Automatic silent upgrades are outside this design.

### Version comparison baseline

The version checker receives an explicit base revision and compares that revision's manifest and generated plugin tree with the candidate tree:

- Initial release: if the base revision has no plugin manifest, version `0.1.0` is accepted.
- Pull request CI: use `github.event.pull_request.base.sha`, so a multi-commit PR is compared with its target branch state.
- Push CI: use `github.event.before`; an all-zero creation SHA is treated as an initial release.
- Local working-tree validation: default to `HEAD`, comparing committed state with working-tree output; callers may pass `--base-ref <revision>` explicitly.

If bundled output or the dependency lock changes, the candidate manifest version must be a valid SemVer value greater than the baseline version. Marketplace metadata does not duplicate the plugin version.

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
3. a clean `bundle/` rebuild comparison;
4. plugin manifest and marketplace validation;
5. a secret scan limited to the changed plugin artifacts, using Gitleaks pinned to an immutable action commit in the workflow.

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

- `plugins/vibecoding-guidance/.codex-plugin/plugin.json` is valid and points to `./bundle/skills/`.
- The generated plugin contains both local skills and the complete locked Superpowers closure.
- The plugin contains no unresolved required `superpowers:` references.
- Superpowers copyright and MIT license are included.
- Adding an undeclared dependency causes a clear test or validation failure.
- Rebuilding from the same lock produces the same plugin contents.
- Marketplace metadata resolves to the plugin directory in the GitHub repository.
- README documents marketplace installation and upgrades.
- All tests and validation commands pass before the plugin is pushed.
