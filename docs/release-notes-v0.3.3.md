# Release Notes — v0.3.3

## Summary

This release continues the OpenClaw dashboard productization work and upgrades the Web UI from a single-team view into a more practical **multi-team command center**.

## Highlights

- Added a homepage **Team overview board**
- Added automatic homepage refresh for overview data
- Added a built-in **cleanup current team** action in the header
- Added browser-local dashboard settings
- Synchronized custom dashboard title with the browser tab title
- Continued Simplified Chinese localization of the overview experience

## What changed

### Web UI
- Homepage can now act as a true command center instead of only a team detail launcher
- Teams can be clicked directly from the overview board to enter the corresponding team dashboard
- Overview visibility now respects:
  - teams per row
  - max visible teams
- Header settings are stored locally in the browser via local storage

### UX improvements
- Homepage connection state no longer appears disconnected just because no team is currently open
- Team cleanup no longer requires going back to CLI for common cleanup workflows
- Browser tab title now matches the configured dashboard title

## Recommended usage

Use `clawteam board serve` and open:

```text
http://<LAN-IP>:8090
```

Then configure the dashboard from the built-in settings panel.
