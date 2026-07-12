# Verification and release gate

Load this file only after implementation tasks are complete or when the user explicitly asks to prepare a release.

## Product acceptance

1. Map every acceptance criterion to fresh automated or manual evidence.
2. Exercise the primary user journey and applicable first-use, empty, loading, error, permission, recovery, and destructive-action paths.
3. Verify build/package output, configuration, migrations, security boundaries, and required documentation.
4. List any blocked, cancelled, deferred, or manually unverified item. Never hide it behind an overall success statement.
5. Present results and obtain explicit user acceptance.

Do not release when a required acceptance criterion or critical task remains blocked.

## Release plan

Before requesting deployment authorization, state:

- Exact target environment and release artifact/version.
- Required secrets and configuration without exposing secret values.
- Data migration and backup steps, when applicable.
- Rollback trigger and exact rollback method.
- Post-release smoke checks, health signals, logs, and monitoring window.

Use the project's existing deployment method or an applicable deployment Skill. Do not introduce a new platform or pipeline without approval.

## Authorization and completion

Deployment, publishing, migration, or another external write requires explicit user authorization immediately before execution. After release, run the planned smoke checks and inspect health evidence. If checks fail, stop, report evidence, and follow the approved rollback plan; do not improvise destructive recovery.

Record release verification in the final HTML phase and commit it as its own approved task node. A release is complete only when the deployed result—not merely the local build—passes the agreed checks.

