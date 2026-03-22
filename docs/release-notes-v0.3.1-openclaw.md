# Release Notes — v0.3.1-openclaw

## Summary

This release turns the OpenClaw fork from an installation-only experiment into a **validated multi-agent workflow build**.

The biggest functional improvement is a fix for the leader synthesis gap: when a leader-owned synthesis task becomes unblocked, ClawTeam can now auto-spawn the leader to complete the final summary stage.

## Highlights

- Verified **single-worker execution** with OpenClaw
- Verified **two-worker parallel execution**
- Verified **dependency resolution** using `--blocked-by`
- Fixed and verified **leader auto-synthesis** after dependency release
- Added live validation notes for OpenClaw users

## What changed

### Functional fix
- Added a minimal orchestration trigger in `clawteam/team/tasks.py`
- When a blocked task becomes pending and its owner is the team leader, ClawTeam now attempts to auto-spawn a leader agent to complete synthesis work

### Documentation improvements
- Added **Verified OpenClaw Flows** section to `README.md`
- Added `docs/openclaw-validation.md`
- Added initial maintenance assets (`CHANGELOG.md`, issue templates, release notes draft)

## Practical impact

This release means the fork has now been demonstrated to support:

1. Worker spawn in real OpenClaw sessions
2. Multi-worker task execution in parallel
3. Dependency-based task coordination
4. Final leader-side synthesis without manual re-triggering

## Known caveats

- Session persistence behavior may still need additional polish depending on runtime session ID visibility
- Further stress testing is recommended for larger teams and longer-running workflows

## Recommended next validation steps

- 3+ worker stress tests
- multi-level dependency chains
- failure recovery and retry behavior
- longer-running synthesis tasks
