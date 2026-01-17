# Claude Orchestrator

SPEC lifecycle management and project orchestration with Ralph Engine integration.

## Features

- **Git Branch-Based Status Detection**: Automatically track SPEC progress from git branches
- **Dependency Resolution**: Handle SPEC dependencies intelligently
- **Velocity Analytics**: Track completion speed and estimate finish dates
- **Ralph Engine Integration**: Auto-sync when tasks complete

## Requirements

- Claude Code CLI
- Python 3.10+
- Git repository

## Installation

Clone or download this plugin to your preferred location:

```bash
git clone https://github.com/web24365/claude-orchestrator.git
```

## Usage

```bash
# Initialize and discover all SPECs
/moai:orchestrator init

# Show project status
/moai:orchestrator report

# Sync with git branches
/moai:orchestrator git-sync

# Get next recommended task
/moai:orchestrator next

# Show velocity analytics
/moai:orchestrator velocity

# Manually update status
/moai:orchestrator update SPEC-FE-001 completed
```

## Commands

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

## Project Structure

```
claude-orchestrator/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── agents/
│   └── moai-orchestrator.md # Agent definition
├── commands/
│   └── orchestrator.md      # Command definition
├── hooks/
│   └── hooks.json           # Session hooks
├── skills/
│   └── moai-orchestrator/
│       ├── SKILL.md         # Skill documentation
│       └── orchestrator.py  # Core implementation
├── LICENSE
└── README.md
```

## License

MIT

## Author

web24365
