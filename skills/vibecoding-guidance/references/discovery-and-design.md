# Discovery and design gate

Load this file only during requirements, product/UX design, and technical design.

## Interview discipline

1. Inspect the repository, existing docs, constraints, and tests first.
2. Summarize what is known, what is assumed, and what remains open.
3. Ask one question per message only when its answer can materially change scope, behavior, experience, architecture, acceptance, cost, or release risk.
4. Record every temporary default as an explicit assumption. Do not convert silence into approval.
5. When the user changes an earlier answer, update affected sections and call out the consequence.

Do not interrogate the user about facts available from the repository. Do not ask implementation-detail questions that Codex can decide safely after the user has established product constraints.

## Product and usability specification

Write `docs/product-spec.md` in plain language and cover only applicable items:

- Problem and intended users.
- Core value and measurable success.
- Goals, non-goals, constraints, and compliance boundaries.
- Primary end-to-end user journey.
- First use, empty, loading, success, error, permission, and recovery states.
- Destructive actions, confirmation, cancellation, and undo where relevant.
- Accessibility, device/layout, latency, offline, and privacy expectations where relevant.
- Explicit assumptions and unresolved questions.
- Numbered acceptance criteria (`AC-001`, `AC-002`, ...), observable by a user or a test.

Present product and UX sections in small reviewable parts. Revise until the user explicitly approves the written specification.

## Technical design

Write `docs/technical-design.md` after product/UX approval:

1. Describe two or three viable approaches with trade-offs and a recommendation.
2. Define the chosen components, responsibilities, interfaces, and data flow.
3. Define persistence, external integrations, error handling, security/privacy boundaries, and operational constraints only when required.
4. Identify how each acceptance criterion will be verified at the highest practical seam.
5. Define build, test, deployment, rollback, and observability shape appropriate to the project.
6. Check the design against every acceptance criterion, non-goal, and constraint; surface inconsistencies instead of guessing.

Obtain explicit user approval before delivery planning.

