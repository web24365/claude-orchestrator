---
name: moai:orchestrate
description: SPEC lifecycle management and project orchestration
argument-hint: install | init | status | next | audit | git-sync | report | velocity | update [SPEC_ID] [STATUS]
allowed-tools:
  - Bash
  - Task
  - AskUserQuestion
model: inherit
---

# /moai:orchestrate

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
| `install` | Install Orchestrator to current project from templates |
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
# Install Orchestrator to current project
/moai:orchestrate install

# Show project status
/moai:orchestrate report

# Sync with git branches
/moai:orchestrate git-sync

# Get next recommended task
/moai:orchestrate next

# Update status manually
/moai:orchestrate update SPEC-FE-006 completed
```

## Install Subcommand

The `install` subcommand copies Orchestrator files from the template directory to the project:

```bash
/moai:orchestrate install
```

This will:
1. Copy command file to `.claude/commands/orchestrator.md`
2. Copy agent file to `.claude/agents/moai-orchestrator.md`
3. Copy skill files to `.claude/skills/moai-orchestrator/`
4. Copy hook file to `.claude/hooks/moai/session_end__orchestrator_sync.py`
5. Initialize `.moai/indexes/spec-status.json`

## Implementation

Delegates to the Python script: `.claude/skills/moai-orchestrator/orchestrator.py`
