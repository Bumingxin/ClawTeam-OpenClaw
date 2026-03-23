# Local Release Note Draft — Agent Resume / Idle TUI Recovery (2026-03-23)

## Summary

This local-only patch fixes a major coordination reliability issue in ClawTeam's template-driven multi-agent workflows:

- Agents that had already started once could enter an **idle OpenClaw TUI session**
- Later inbox messages would arrive successfully
- But the agent would not reliably resume to consume those messages and finish its task

The fix has now been validated locally on a clean hedge-fund template run.

## What was fixed

### 1. Resume on key inbox messages
Mailbox-triggered recovery is no longer limited to the leader. It now applies to inbox-driven agents more generally when they receive key messages such as:

- `SIGNAL:`
- `RISK REPORT:`
- `All tasks completed.`
- `FINAL:`
- `Need help:`

### 2. Reuse existing saved agent sessions
If the recipient agent has a saved session, ClawTeam now prefers resuming that session instead of assuming a fresh spawn is required.

### 3. Recover alive-but-idle tmux/TUI agents
If an agent process is technically alive but sitting idle inside tmux without a reusable saved session, ClawTeam now injects a fresh prompt into the existing tmux pane as a local fallback.

This addresses the critical gap where:

- process liveness was `true`
- but practical progress was `stalled`

## Validation result

A clean verification team was launched locally:

- Team: `verify-hf-clean-112923`
- Template: `hedge-fund`
- Goal: minimal placeholder workflow validation

Final result:

- **7 / 7 tasks completed**
- Analysts completed
- `risk-manager` resumed and completed
- `portfolio-manager` resumed and completed

## Remaining observation

One intermediate run showed that message arrival vs. message-consumption awareness may still have edge-case instability in some aggregator flows. However, this no longer blocks final workflow closure in the validated clean run.

## Status

- Local patch: complete
- Local verification: complete
- GitHub push: intentionally not performed
