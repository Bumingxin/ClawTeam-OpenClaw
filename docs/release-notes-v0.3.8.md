# Release Notes — v0.3.8 (2026-03-24)

## Summary

This release introduces a production-safe final-report completion path for ClawTeam.
Users can now require a run to finish only after all tasks are complete **and** a final report has been sent.

## What's New

- `clawteam task wait` now supports:
  - `--final-report`
  - `--reporter <agent>` (default: `reviewer`)
  - `--takeover` / `--no-takeover`
- New finalization module: `clawteam/team/finalizer.py`
  - Idempotent delivery with persisted state (`final_report.json`)
  - Reporter-first extraction
  - Optional takeover synthesis when reporter output is missing
- `clawteam launch` now supports:
  - `--wait-final-report`
  - `--reporter`
  - `--takeover` / `--no-takeover`

## Why

Previously, teams could finish tasks but still fail to emit a guaranteed final report to the leader channel.
This release closes that reliability gap and provides explicit, scriptable completion semantics.

## Recommended Usage

```bash
# Start then block until final report is delivered
clawteam launch hedge-fund --team-name fund1 --wait-final-report --reporter reviewer --takeover

# Or existing team:
clawteam task wait fund1 --final-report --reporter reviewer --takeover
```

## Validation

Validated on both paths:
1. Reporter-present path (`mode=reviewer`)
2. Reporter-missing path with takeover (`mode=takeover`)

