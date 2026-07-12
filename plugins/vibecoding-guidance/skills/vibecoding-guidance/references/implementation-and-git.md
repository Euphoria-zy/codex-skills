# Implementation and Git gate

Load this file only while planning, implementing, resuming, or handling blockers.

## Plan task contract

Each task must be independently implementable and verifiable, and include:

- Stable ID such as `P2-03`.
- Status: `待做`, `进行中`, `已完成`, `阻塞`, or `取消`.
- Short outcome-oriented title.
- Dependencies by task ID.
- Exact scope and explicit exclusions where useful.
- Acceptance criteria IDs and task-specific verification.
- Expected files or boundaries.

Split a task if it cannot produce one coherent, passing commit. Do not split documentation, tests, and implementation that must change together to satisfy one behavior.

Create `docs/implementation-plan.md`, then copy `assets/implementation-progress.html` to `docs/<project-name>实施进度.html` and replace its placeholders. The Markdown plan is detailed execution guidance; the HTML is the human-facing status ledger. Keep task IDs and meaning identical.

## Resume and preflight

Before implementation or after interruption:

1. Read the approved specs, plan, and progress HTML.
2. Inspect `git status`, the current branch, and recent task-ID commits.
3. Reconcile any mismatch before editing code.
4. Existing uncommitted changes require a user decision before work begins.
5. A task marked `进行中` without a matching completion commit is interrupted work; inspect it, do not assume success.

## Exact task loop

For the next unblocked task whose dependencies are complete:

1. Change only its HTML status to `进行中` and update the timestamp.
2. Restate its acceptance and verification target.
3. For behavior changes, write the failing test and verify the expected failure.
4. Implement the smallest change that satisfies the task. Do not begin later tasks or unrelated refactors.
5. Run the task-specific check, then the smallest relevant regression set. Read full output and exit status.
6. Compare observable behavior with every mapped acceptance criterion.
7. On success, set HTML status to `已完成`; record verification evidence and completion time.
8. Inspect the diff. Stage only the task's code, tests, required docs, and HTML using explicit paths. Never use `git add .` or `git add -A`.
9. Inspect the staged diff and confirm no unrelated or secret material is present.
10. Commit once with `<type>(<task-id>): <outcome>`, for example `feat(P2-03): persist task schedule`.
11. Confirm the commit exists and the working directory is clean, then continue automatically.

Use the task ID—not a commit hash—as the stable link between plan, HTML, and Git. Find history with `git log --grep=<task-id>`.

## Blocked, failed, and cancelled tasks

If implementation or verification cannot complete:

1. Set status to `阻塞` and record the exact cause, attempted verification, output summary, and what would unblock it.
2. Stage and commit only the progress HTML with `docs(<task-id>): record blocker`.
3. Do not include unverified functional changes in that commit.
4. Do not clean, reset, stash, or discard partial work automatically.
5. Stop the task and every dependent task; ask the user how to proceed.

Use `取消` only after the user approves a scope change. Update the product spec, technical design, plan, and affected dependencies before committing the cancellation.

## Plan changes

Implementation may reveal a missing or incorrect requirement. Do not silently edit history to match the code. Stop, explain the gap, revise affected approved artifacts, obtain approval, then add or change task rows. Preserve completed task IDs and Git history.
