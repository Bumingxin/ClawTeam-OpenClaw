# Release Notes — v0.3.5

## Summary

This release focuses on two areas that were validated in real usage:

1. **ClawTeam coordination reliability** for OpenClaw-driven teams
2. **Web UI large-screen usability** for command-center / LED display scenarios

The result is a significantly more robust multi-agent workflow and a more practical dashboard for monitoring active teams.

## Highlights

- Fixed idle-agent resume failures in template-based ClawTeam workflows
- Validated end-to-end automatic closure on a clean hedge-fund team run
- Improved Web UI to better fill browser width on large displays
- Added a detail-page Team hero layout with a highlighted current team and compact side cards
- Fixed dashboard timestamps to display in browser-local time
- Fixed rendering artifacts and layout issues introduced during dashboard tuning

## What changed

### Coordination reliability
- Inbox-driven agents no longer depend only on a one-shot turn model
- When key messages arrive, ClawTeam now attempts layered recovery:
  - resume a saved OpenClaw session first
  - fall back to tmux/TUI prompt injection when the agent is alive but idle
  - fall back to spawning a new turn when needed
- This fix was validated on a clean `hedge-fund` template workflow with all 7 tasks reaching `completed`

### Web UI layout
- Main dashboard layout is now more fluid and browser-width-aware
- Overview and dashboard card grids use more adaptive sizing
- Detail page now shows:
  - the currently selected team as a large primary card
  - up to 6 other teams as smaller cards on the right
- Task board columns remain on one row instead of wrapping unexpectedly

### Dashboard polish fixes
- Removed stray HTML tail fragments that could render visible garbage characters
- Corrected timestamp rendering to use browser-local timezone instead of raw ISO string slicing
- Reduced over-aggressive vertical stretching that created large empty blank areas

## Practical impact

This release makes ClawTeam substantially more reliable for OpenClaw-led multi-agent orchestration while also improving live dashboard readability on wide desktop monitors and LED displays.

## Notes

- This release includes OpenClaw-first validation and UI tuning work from the local production fork
- Additional message-consumption awareness refinements may still be added in future versions, but the main closure bug is fixed and validated
