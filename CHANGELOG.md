# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project generally follows semantic versioning in spirit, even when release tags are still evolving.

## [0.3.1-openclaw] - 2026-03-22

### Added
- Added a **Verified OpenClaw Flows** section to `README.md` so users can see which workflows have been validated in a live OpenClaw environment.
- Added `docs/openclaw-validation.md` documenting real-world validation of:
  - single-worker execution
  - two-worker parallel execution
  - dependency resolution
  - leader synthesis workflow
- Added initial project-maintenance assets:
  - `CHANGELOG.md`
  - GitHub issue templates for bug reports and feature requests
  - release-notes draft for the first validated OpenClaw release

### Fixed
- Fixed a core OpenClaw orchestration gap where a leader-owned synthesis task could become unblocked but would not automatically execute.
- Added an auto-trigger path so that when a leader-owned blocked task becomes pending, ClawTeam can auto-spawn a leader agent to perform synthesis and close the task loop.

### Validated
- Confirmed that OpenClaw workers can receive tasks, execute them, report back, and complete tasks through ClawTeam.
- Confirmed two-worker parallel execution using isolated workspaces and tmux sessions.
- Confirmed blocked dependency chains resolve correctly after upstream task completion.
- Confirmed leader auto-synthesis works after the unblocked-task trigger fix.

### Notes
- `session save` behavior may still depend on how reliably runtime session identifiers are exposed in the active OpenClaw environment.
- Additional stress testing is still recommended for 3+ workers, multi-level dependencies, long-running jobs, and failure recovery.
