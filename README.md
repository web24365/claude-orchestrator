# Claude Orchestrator

SPEC lifecycle management and project orchestration with Ralph Engine integration.

## Features

- **Git Branch-Based Status Detection**: Automatically track SPEC progress from git branches
- **Dependency Resolution**: Handle SPEC dependencies intelligently
- **Velocity Analytics**: Track completion speed and estimate finish dates
- **Ralph Engine Integration**: Auto-sync when tasks complete

## Installation

```bash
/plugin install web24365/claude-orchestrator
```

## Usage

```bash
# Initialize SPEC tracking
/claude-orchestrator:install

# Show project status
/claude-orchestrator:report

# Sync with git branches
/claude-orchestrator:git-sync

# Get next recommended task
/claude-orchestrator:next

# Show velocity analytics
/claude-orchestrator:velocity
```

## Commands

| Command | Description |
|---------|-------------|
| `install` | Install Orchestrator to current project |
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

## License

MIT

## Author

web24365
