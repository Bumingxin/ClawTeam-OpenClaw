# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project generally follows semantic versioning in spirit, even when release tags are still evolving.

## [0.3.6] - 2026-03-23

### Added
- Added Simplified Chinese-first coordination defaults for ClawTeam message flow, so internal inbox/event-stream summaries now prefer Chinese by default instead of English.
- Added Chinese resume-trigger prefixes in mailbox handling, including messages such as `任务已完成：`, `最终汇总：`, `风险报告：`, `需要协助：` and other common specialist summary labels.
- Added duplicate-spawn protection for tmux-backed agents so the same team/agent pair is not launched repeatedly when an active runtime already exists.

### Changed
- Team runtime cleanup now distinguishes more clearly between **releasing runtime** and **deleting team data**: when a team fully completes, tmux/OpenClaw runtime is released immediately while task/team data remains available for review until explicit cleanup.
- Default coordination guidance for spawned agents now explicitly instructs them to use Simplified Chinese for internal collaboration messages unless the user requests another language.
- Common OpenClaw-facing templates (`hedge-fund`, `strategy-room`, `code-review`, `research-paper`) now use Chinese-first message examples for specialist summaries and final handoff messages.

### Fixed
- Fixed the issue where `team cleanup` could delete ClawTeam data directories but leave `tmux` / `openclaw-tui` runtime processes behind.
- Fixed the issue where a team could reach full `completed` task state but still keep its tmux session alive because runtime-release logic was only attached to dependency-unblock paths.
- Fixed the issue where the same agent could be spawned multiple times into duplicate tmux windows during wake/resume races.
- Fixed the issue where message flow in the dashboard remained English-heavy even after the Web UI itself had been localized to Simplified Chinese.

## [0.3.5] - 2026-03-23

### Added
- Added local release-note draft for the agent resume / idle-TUI recovery fix.
- Added a detail-page-specific Team hero layout: current team highlighted as a large primary card, with other teams shown as compact cards on the right.

### Changed
- Web UI now uses a more fluid, browser-width-aware layout instead of being constrained to a fixed central width.
- Detail page top area now separates the selected team from other teams to improve command-center readability on wide screens and LED displays.
- Message timestamps in the dashboard now render using browser-local time instead of slicing raw ISO strings.

### Fixed
- Fixed a critical coordination issue where inbox-driven agents (including leader and aggregator roles like `risk-manager`) could go idle and fail to resume when later messages arrived.
- Fixed the case where an agent could be alive in tmux/OpenClaw TUI but practically stalled; added layered recovery via saved-session resume and tmux prompt injection fallback.
- Fixed detail-page rendering breakage caused by missing style definitions for the new Team hero component.
- Fixed stray HTML tail fragments that could render literal garbage characters at the bottom of the dashboard.
- Fixed dashboard task columns to stay on a single row instead of wrapping when the browser is resized.
- Fixed message stream timestamps to respect the browser's local timezone.
- Reduced over-aggressive vertical min-height behavior that created large empty gaps in overview/detail pages.

## [0.3.4] - 2026-03-22

### Added
- Added display-layer Simplified Chinese translation for more team/task/role text in the dashboard.
- Added homepage brand click behavior to return directly to the overview page.

### Changed
- Homepage now always prefers the overview landing page instead of auto-entering a team when only one team exists.
- Overview board content is now more consistently localized for Chinese-first usage.

### Fixed
- Fixed the issue where the homepage could still auto-open a single team instead of staying on the overview page.
- Improved readability of team descriptions, member roles, and task subjects through display-layer translation.

## [0.3.3] - 2026-03-22

### Added
- Added homepage **Team overview board** support so users can see multiple teams from the landing page and click into a team directly.
- Added a **cleanup current team** action directly inside the Web UI header.
- Added browser-local dashboard settings for:
  - custom dashboard title
  - teams per row on the overview board
  - max visible teams on the overview board

### Changed
- Homepage overview now refreshes automatically.
- The overview board now follows the configured display limits more intuitively and keeps teams in the main card grid instead of prematurely splitting them into a list.
- Dashboard title customization now also updates the browser tab title for consistency.
- More of the dashboard overview UI is now consistently translated into Simplified Chinese.

### Fixed
- Fixed the issue where the homepage could appear disconnected until a specific team was opened.
- Fixed the mismatch between the custom dashboard title and the browser tab title.

## [0.3.2] - 2026-03-22

### Added
- Added a LAN-ready Web UI default for OpenClaw-first usage.
- Added a command-center style Simplified Chinese dashboard experience for team monitoring.
- Added documented Web UI defaults in both English and Chinese README files.

### Changed
- Default Web UI host is now `0.0.0.0`.
- Default Web UI port is now `8090`.
- The dashboard layout now uses a more visual command-center structure:
  - top command bar
  - core battle-state cards
  - member status panel
  - task battle-board
  - message/event stream

### Fixed
- Improved team selector contrast and dropdown readability in the Web UI.
- Strengthened status expression for blocked tasks, important messages, and live connection feedback.

### Notes
- This release builds on the previously validated OpenClaw task orchestration line and packages the current LAN-accessible Chinese Web UI improvements into a formal release.

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
- Added a Simplified Chinese README (`README.zh-CN.md`) and language switcher links in the main README.
- Added a localized, command-center style Chinese Web UI tuned for OpenClaw team monitoring.

### Changed
- Changed Web UI defaults from loopback-only `127.0.0.1:8080` to LAN-friendly `0.0.0.0:8090`.
- Upgraded the dashboard layout into a three-column command-center style cockpit with stronger status emphasis, member visibility, task battle-board layout, and highlighted event flow.

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
