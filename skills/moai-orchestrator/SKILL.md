---
name: moai-orchestrator
description: SPEC lifecycle management and project orchestration for MoAI workflow
version: 1.1.0
user-invocable: false
triggers:
  - spec status
  - spec lifecycle
  - orchestrator
  - roadmap
  - project progress
tools:
  - Bash
  - Read
---

# MoAI Orchestrator Skill

This skill provides SPEC lifecycle management capabilities for MoAI projects.

## Overview

The orchestrator manages the development lifecycle of SPEC documents found in `.moai/specs/`.

## Integration with Ralph Engine

When Ralph Engine completes a task (detects `<promise>DONE</promise>`), the `session_end__orchestrator_sync.py` hook automatically calls:

```bash
python .claude/skills/moai-orchestrator/orchestrator.py update [SPEC_ID] completed
```

This ensures that spec-status.json stays synchronized with actual completion status.

## Core Capabilities

### Available Commands

Execute via the Python script in this skill directory:

- `init`: Initialize roadmap and discover specs from `.moai/specs/`
- `git-sync`: Auto-update status based on git feature branches
- `status`: Show current spec status (ASCII format)
- `report`: Generate markdown progress report
- `next`: Recommend next actionable spec (respects dependencies)
- `audit`: Scan for implementation anomalies
- `velocity`: Show velocity analytics, projections, and bottleneck detection
- `update [SPEC_ID] [STATUS]`: Manually update spec status

### Velocity Analytics

The `velocity` command provides:

- Completion metrics (average time, fastest/slowest SPEC)
- Weekly trend (completions per week for last 4 weeks)
- Projection (estimated completion date based on historical data)
- Bottleneck detection (stale in-progress items, blocked dependencies)

### Status Values

- `pending`: Not started
- `in_progress`: Currently being worked on
- `verification`: Implementation complete, awaiting verification
- `completed`: Fully implemented and verified

## Usage

### Script Execution

```bash
python .claude/skills/moai-orchestrator/orchestrator.py <command>
```

### Typical Workflow

1. Run `git-sync` to detect branch-based progress
2. Run `init` to discover new specs
3. Run `audit` to check for anomalies
4. Run `report` to generate status dashboard

## Data Files

- Status tracking: `.moai/indexes/spec-status.json`
- Spec definitions: `.moai/specs/SPEC-*/spec.md`

## Dependencies

- Git repository with feature branch naming: `feature/SPEC-XXX`
- SPEC documents with YAML frontmatter containing `dependencies:` field
