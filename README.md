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

### Option 1: Plugin Marketplace (Recommended)

```bash
# Add marketplace
/plugin marketplace add web24365/claude-orchestrator

# Install plugin
/plugin install claude-orchestrator@web24365-claude-orchestrator
```

**Scope options:**

| Scope | Description |
|-------|-------------|
| `--scope user` | Available in all projects (default) |
| `--scope project` | Shared with team (`.claude/settings.json`) |
| `--scope local` | Local only (gitignored) |

### Option 2: Manual Installation

```bash
git clone https://github.com/web24365/claude-orchestrator.git /tmp/claude-orchestrator

# Copy to your project's .claude directory
cp -r /tmp/claude-orchestrator/commands/* .claude/commands/
cp -r /tmp/claude-orchestrator/agents/* .claude/agents/
cp -r /tmp/claude-orchestrator/skills/* .claude/skills/
cp -r /tmp/claude-orchestrator/hooks/* .claude/hooks/
```

### Option 3: Development Testing

```bash
claude --plugin-dir /path/to/claude-orchestrator
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
