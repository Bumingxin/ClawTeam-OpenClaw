# Release Notes — v0.3.6

## Summary

This release closes several real-world OpenClaw lifecycle gaps discovered during live use and pushes ClawTeam further toward a production-ready command-center workflow.

The focus of `v0.3.6` is threefold:

1. **completed teams must release runtime immediately**
2. **active agents must not be spawned twice into duplicate tmux windows**
3. **message flow in the dashboard should default to Simplified Chinese, not just the UI chrome**

## Highlights

- Added automatic tmux/runtime release when a team fully completes
- Fixed `team cleanup` so it also releases tmux / `openclaw-tui` runtime instead of only deleting metadata
- Added duplicate-spawn protection for tmux-backed agents
- Switched default internal coordination message flow to **Simplified Chinese-first**
- Localized key template message formats for:
  - `hedge-fund`
  - `strategy-room`
  - `code-review`
  - `research-paper`

## What changed

### Runtime lifecycle
- `team cleanup` now performs best-effort tmux session teardown before deleting team/task/session data
- when the final team task is marked `completed`, ClawTeam now releases the tmux session immediately
- completion-time runtime release is now triggered from the **generic completed-task path**, not only from dependency-resolution paths

### Duplicate spawn protection
- tmux backend now checks whether a team/agent runtime is already alive before launching a new one
- stale registry state is reconciled against real tmux windows before deciding whether to spawn again
- resume/wake races are now much less likely to create duplicate agent windows

### Chinese-first message flow
- spawned agents are now explicitly instructed to use Simplified Chinese for internal coordination messages by default
- mailbox resume-trigger logic now recognizes Chinese prefixes such as:
  - `任务已完成：`
  - `最终汇总：`
  - `风险报告：`
  - `需要协助：`
  - `系统：`
  - `交付：`
  - `风险：`
  - `备忘录：`
  - `安全：`
  - `性能：`
  - `架构：`
  - `文献：`
  - `方法：`
  - `结果：`
  - `信号：`
- common templates now emit Chinese-first specialist summaries and final handoff messages

## Validation notes

These fixes were driven by live OpenClaw usage and verified against real failure modes:

- duplicate `openclaw-tui` residue after team completion
- `team cleanup` appearing to remove teams from the UI while leaving runtime alive
- duplicate tmux windows for the same agent under wake/resume conditions
- English-heavy message flow in the dashboard even when the Web UI was already Chinese-localized

A minimal regression run confirmed:
- duplicate spawn prevention works
- final task completion now releases tmux runtime correctly

## Recommended follow-up

After upgrading to `v0.3.6`, recommended next checks are:

- test one completed team and confirm no residual `openclaw-tui` remains
- test wake/resume on an inbox-driven leader role
- test one dashboard workflow using a Chinese-first template and verify the message stream is readable end-to-end
