---
name: vibecoding-guidance
description: Use when starting or substantially changing software and the work risks ambiguous requirements, silent assumptions, usability drift, multi-step implementation, weak progress visibility, or untraceable Git history.
---

# VibeCoding Guidance

## Overview

Turn user intent into approved, traceable software delivery. Treat approved artifacts as contracts: clarify before deciding, implement one accepted task at a time, and prove results before claiming completion.

## Non-negotiable rules

- Ask one material question per message. Never silently invent product, UX, architecture, or release decisions.
- Inspect existing code and documents before asking what they already answer.
- Do not implement until the user has approved product/UX design, technical design, and the detailed implementation plan.
- After plan approval, continue automatically. Pause only for a blocker, material ambiguity, approved-design deviation, existing uncommitted changes, or risky external action.
- Keep durable state in repository artifacts, not chat memory. On resume, reconcile the specs, progress HTML, Git history, and working directory before acting.
- Scale artifact detail to the project, but never skip a gate because the request sounds simple.

## Workflow

### 1. Discover and design

Read [references/discovery-and-design.md](references/discovery-and-design.md) completely.

**REQUIRED SUB-SKILL:** Use `vibecoding-guidance:brainstorming` for the dialogue while satisfying this Skill's product and usability outputs. The user resolves choices that materially change behavior.

Produce approved `docs/product-spec.md` and `docs/technical-design.md`. Later changes require impact analysis and renewed approval.

### 2. Plan delivery

**REQUIRED SUB-SKILL:** Use `vibecoding-guidance:writing-plans` after design approval.

Read [references/implementation-and-git.md](references/implementation-and-git.md) completely. Create `docs/implementation-plan.md` and copy [assets/implementation-progress.html](assets/implementation-progress.html) to `docs/<project-name>实施进度.html`.

Every HTML task row is one delivery node and one future Git commit. Present the complete plan and wait for explicit user approval.

### 3. Establish Git safety

- New project: initialize Git and create `chore: establish project baseline` before task implementation.
- Existing project: work directly on its primary branch; do not create a feature branch or worktree.
- If tracked or untracked changes already exist, stop and ask the user how to handle them. Never commit, stash, discard, or absorb them automatically.

### 4. Execute task nodes

Follow the exact task loop in `references/implementation-and-git.md`.

**REQUIRED SUB-SKILLS:** Use `vibecoding-guidance:test-driven-development` for behavior changes and `vibecoding-guidance:coding-standards` for the minimal implementation. Use `vibecoding-guidance:systematic-debugging` when behavior is unexpected.

For each task: mark in progress, implement only its acceptance, verify, update HTML, stage explicit paths, and commit once with its task ID. If blocked, commit only blocker evidence in the progress document, stop dependent work, and ask the user.

### 5. Verify and release

**REQUIRED SUB-SKILL:** Use `vibecoding-guidance:verification-before-completion` before any completion claim.

Check every acceptance criterion against fresh evidence and obtain user acceptance. Then read [references/release.md](references/release.md) completely. Deployment or another external side effect requires explicit authorization, a rollback method, and post-release verification.

## Red flags

Stop on silent product decisions, code before approvals, completion without acceptance evidence, unrelated staged files, blocked dependencies, or unapproved plan drift.
