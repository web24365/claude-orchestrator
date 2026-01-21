#!/usr/bin/env python3
"""
Session End Hook: Orchestrator Sync

Detects <promise>DONE</promise> markers in conversation context
and updates spec-status.json accordingly.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def find_orchestrator_script() -> Path | None:
    """Find orchestrator.py in plugin directory."""
    # Check CLAUDE_PLUGIN_ROOT first
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        script = Path(plugin_root) / "skills" / "moai-orchestrator" / "orchestrator.py"
        if script.exists():
            return script

    # Fallback: search in common locations
    possible_paths = [
        Path.home() / ".claude" / "plugins" / "cache" / "web24365-claude-orchestrator"
        / "claude-orchestrator" / "1.0.0" / "skills" / "moai-orchestrator" / "orchestrator.py",
        Path(__file__).parent.parent / "skills" / "moai-orchestrator" / "orchestrator.py",
    ]

    for p in possible_paths:
        if p.exists():
            return p

    return None


def extract_completed_specs(conversation: str) -> list[str]:
    """Extract SPEC IDs from <promise>DONE</promise> markers."""
    completed = []

    # Pattern 1: SPEC-XXX mentioned near DONE marker
    pattern1 = r"(SPEC-[A-Z0-9-]+)[^<]*<promise>DONE</promise>"
    matches1 = re.findall(pattern1, conversation, re.IGNORECASE)
    completed.extend(matches1)

    # Pattern 2: DONE marker with SPEC reference
    pattern2 = r"<promise>DONE</promise>[^S]*(SPEC-[A-Z0-9-]+)"
    matches2 = re.findall(pattern2, conversation, re.IGNORECASE)
    completed.extend(matches2)

    # Pattern 3: Explicit completion statement
    pattern3 = r"(?:completed|finished|done):\s*(SPEC-[A-Z0-9-]+)"
    matches3 = re.findall(pattern3, conversation, re.IGNORECASE)
    completed.extend(matches3)

    # Deduplicate and uppercase
    return list(set(s.upper() for s in completed))


def update_spec_status(spec_id: str, orchestrator_script: Path) -> bool:
    """Update spec status to completed using orchestrator."""
    try:
        result = subprocess.run(
            ["python3", str(orchestrator_script), "update", spec_id, "completed"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"✅ Updated {spec_id} to completed")
            return True
        else:
            print(f"⚠️ Failed to update {spec_id}: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Error updating {spec_id}: {e}", file=sys.stderr)
        return False


def main():
    """Main hook entry point."""
    # Read hook input from stdin (JSON format)
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.stdin.seek(0)
        hook_input = {"conversation": sys.stdin.read()}

    # Extract conversation content
    conversation = ""
    if isinstance(hook_input, dict):
        conversation = hook_input.get("conversation", "")
        if not conversation:
            transcript = hook_input.get("transcript", [])
            if isinstance(transcript, list):
                conversation = " ".join(
                    str(msg.get("content", ""))
                    for msg in transcript
                    if isinstance(msg, dict)
                )

    if not conversation:
        sys.exit(0)

    # Check for DONE markers
    if "<promise>DONE</promise>" not in conversation:
        sys.exit(0)

    # Find orchestrator script
    orchestrator = find_orchestrator_script()
    if not orchestrator:
        print("⚠️ Orchestrator script not found", file=sys.stderr)
        sys.exit(0)

    # Extract completed SPECs
    completed_specs = extract_completed_specs(conversation)
    if not completed_specs:
        print("⚠️ DONE marker found but no SPEC ID detected", file=sys.stderr)
        sys.exit(0)

    # Update each completed SPEC
    print(f"🔄 Syncing {len(completed_specs)} completed SPEC(s)...")
    for spec_id in completed_specs:
        update_spec_status(spec_id, orchestrator)

    print("✅ Orchestrator sync complete")


if __name__ == "__main__":
    main()
