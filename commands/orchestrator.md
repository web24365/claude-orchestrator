---
name: moai:orchestrator
description: SPEC lifecycle management and project orchestration
argument-hint: init | status | next | audit | git-sync | report | velocity | update [SPEC_ID] [STATUS]
allowed-tools:
  - Bash
  - Task
  - AskUserQuestion
model: inherit
---

# /moai:orchestrator

This command manages SPEC lifecycle and project orchestration.

## Purpose

Provides project-level SPEC management capabilities:
- Git branch-based status detection
- Dependency resolution
- Velocity analytics and bottleneck detection
- Progress reporting

## Integration with Ralph Engine

When Ralph Engine completes a task (detects `<promise>DONE</promise>`),
the `session_end__orchestrator_sync.py` hook automatically updates
`spec-status.json` via this orchestrator.

## Subcommands

| Command | Description |
|---------|-------------|
| `init` | Initialize roadmap and discover all SPECs |
| `git-sync` | Auto-update status based on git branches |
| `status` | Show current status (ASCII format) |
| `report` | Generate weekly markdown report |
| `next` | Recommend next action (respects dependencies) |
| `audit` | Scan for implementation anomalies |
| `velocity` | Show analytics and completion projections |
| `update [SPEC_ID] [STATUS]` | Manually update SPEC status |

## Status Values

- `pending`: Not started
- `in_progress`: Currently being worked on
- `verification`: Implementation complete, awaiting verification
- `completed`: Fully implemented and verified

## Usage

```bash
# Initialize and discover SPECs
/moai:orchestrator init

# Show project status
/moai:orchestrator report

# Sync with git branches
/moai:orchestrator git-sync

# Get next recommended task
/moai:orchestrator next

# Update status manually
/moai:orchestrator update SPEC-FE-006 completed
```

## Implementation

Delegates to the Python script: `${CLAUDE_PLUGIN_ROOT}/skills/moai-orchestrator/orchestrator.py`
