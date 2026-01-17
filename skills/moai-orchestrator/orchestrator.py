#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Configuration
# Find project root by looking for .moai directory from current working directory
def _find_project_root() -> Path:
    """Find project root by locating .moai directory from cwd."""
    current = Path.cwd()
    for _ in range(10):  # Max 10 levels up
        if (current / ".moai").is_dir():
            return current / ".moai"
        current = current.parent
    # Fallback to cwd
    return Path.cwd() / ".moai"


MOAI_ROOT = _find_project_root()
SPECS_DIR = MOAI_ROOT / "specs"
STATUS_FILE = MOAI_ROOT / "indexes" / "spec-status.json"


class MoAIOrchestrator:
    def __init__(self):
        self.status_data = self._load_status()

    def _load_status(self) -> dict:
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                    if "specs" not in data or not isinstance(data["specs"], dict):
                        data["specs"] = {}
                    return data
            except json.JSONDecodeError:
                pass
        return self._create_initial_status()

    def _create_initial_status(self) -> dict:
        return {
            "version": "1.1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "specs": {},
        }

    def _save_status(self):
        self.status_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.status_data, f, indent=2, ensure_ascii=False)

    def _parse_dependencies(self, spec_path: Path) -> list[str]:
        spec_file = spec_path / "spec.md"
        if not spec_file.exists():
            return []

        try:
            content = spec_file.read_text(encoding="utf-8")
            # Extract frontmatter
            match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                fm = match.group(1)
                # Look for dependencies: [A, B] or dependencies: \n - A
                dep_match = re.search(r"dependencies:\s*\[(.*?)\]", fm)
                if dep_match:
                    deps = [
                        d.strip() for d in dep_match.group(1).split(",") if d.strip()
                    ]
                    return deps
        except Exception:
            pass
        return []

    def init_roadmap(self):
        print(f"Scanning {SPECS_DIR}...")
        if not SPECS_DIR.exists():
            print("Error: Specs directory not found.", file=sys.stderr)
            return

        found_specs = []
        items = list(SPECS_DIR.rglob("SPEC-*"))

        for item in sorted(items):
            if item.is_dir():
                spec_id = item.name
                found_specs.append(spec_id)
                deps = self._parse_dependencies(item)

                if spec_id not in self.status_data["specs"]:
                    self.status_data["specs"][spec_id] = {
                        "status": "pending",
                        "path": str(item.relative_to(MOAI_ROOT)),
                        "dependencies": deps,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "history": [],
                    }
                else:
                    # Update dependencies even for existing specs
                    self.status_data["specs"][spec_id]["dependencies"] = deps

        self._save_status()
        print(f"Initialized {len(found_specs)} specs.")

    def sync_git(self):
        print("🐙 Syncing with Git branches...")
        try:
            # Fetch prune to get latest remote state
            subprocess.run(["git", "fetch", "--prune"], check=True, capture_output=True)

            # List all branches
            result = subprocess.run(
                ["git", "branch", "-a", "--format=%(refname:short)"],
                check=True,
                capture_output=True,
                text=True,
            )
            branches = result.stdout.splitlines()

            # Find feature branches: feature/SPEC-XXX
            updates = 0
            for branch in branches:
                match = re.search(r"feature/(SPEC-[A-Z0-9-]+)", branch)
                if match:
                    spec_id = match.group(1)
                    if spec_id in self.status_data["specs"]:
                        curr = self.status_data["specs"][spec_id]["status"]
                        if curr == "pending":
                            print(
                                f"  Found branch '{branch}' -> Mark {spec_id} In Progress"
                            )
                            self.update_status(spec_id, "in_progress")
                            updates += 1

            if updates == 0:
                print("  No new status updates from Git.")

        except Exception as e:
            print(f"Error syncing git: {e}", file=sys.stderr)

    def show_report(self):
        specs = self.status_data.get("specs", {})
        total = len(specs)
        stats = {"completed": 0, "in_progress": 0, "verification": 0, "pending": 0}

        for s in specs.values():
            stats[s["status"]] = stats.get(s["status"], 0) + 1

        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        completed_weekly = 0

        print("\n# 📊 MoAI Weekly Report")
        print(f"**Generated**: {now.strftime('%Y-%m-%d %H:%M')}\n")

        print("## Summary")
        print(f"- **Total Specs**: {total}")
        print(
            f"- **Completed**: {stats['completed']} ({(stats['completed'] / total * 100 if total else 0):.1f}%)"
        )
        print(f"- **In Progress**: {stats['in_progress']}")
        print(f"- **Pending**: {stats['pending']}\n")

        print("## Weekly Velocity")
        for _data in specs.values():
            if _data["status"] == "completed":
                # Check history for completion date
                for h in _data.get("history", []):
                    if h["to"] == "completed":
                        ts = datetime.fromisoformat(h["timestamp"])
                        if ts > week_ago:
                            completed_weekly += 1
                            break
        print(f"- **Specs Completed (Last 7 Days)**: {completed_weekly}")

        print("\n## Active Work")
        print("| Spec ID | Status | Dependencies |")
        print("|---------|--------|--------------|")
        for sid, data in sorted(specs.items()):
            if data["status"] != "pending":
                deps = ", ".join(data.get("dependencies", []))
                print(f"| {sid} | {data['status']} | {deps} |")

    def show_status(self):
        # ... existing implementation ...
        self.show_report()  # Reusing report for status is cleaner for now or keep ascii
        pass  # To satisfy valid python

    def status_ascii(self):
        # Renaming original show_status to status_ascii for CLI usage if needed
        specs = self.status_data.get("specs", {})
        total = len(specs)
        if total == 0:
            print("No specs found.")
            return

        completed = sum(1 for s in specs.values() if s["status"] == "completed")
        print("\n=== MoAI Spec Status ===")
        print(f"Progress: {completed}/{total} ({completed / total * 100:.1f}%)")
        print("=" * 60)
        print(f"{'SPEC ID':<30} {'STATUS':<15} {'DEPS'}")
        print("-" * 60)

        for spec_id, data in sorted(specs.items()):
            status = data.get("status", "pending")
            deps = str(len(data.get("dependencies", []))) + " deps"
            print(f"{spec_id:<30} {status:<15} {deps}")
        print("=" * 60)

    def audit_specs(self):
        # ... (Same as before) ...
        print("\n=== Auditing Specs ===")
        specs = self.status_data.get("specs", {})
        candidates = []
        for spec_id, data in sorted(specs.items()):
            spec_path = MOAI_ROOT / data.get("path", "")
            if not spec_path.exists():
                continue

            has_verification = (spec_path / "verification.py").exists()
            status = data.get("status", "pending")

            if status == "pending" and has_verification:
                print(f"⚠️  {spec_id}: Pending but has verification.py")
                candidates.append(spec_id)
        if not candidates:
            print("✅ No anomalies found.")

    def get_next_action(self):
        specs = self.status_data.get("specs", {})
        candidates = []

        for spec_id, data in sorted(specs.items()):
            if data["status"] == "pending":
                # Check dependencies
                deps = data.get("dependencies", [])
                blocked = False
                for d in deps:
                    if d in specs and specs[d]["status"] != "completed":
                        blocked = True
                        break
                if not blocked:
                    candidates.append(spec_id)

        # Priority: In Progress -> Pending (Non-blocked)
        for spec_id, data in specs.items():
            if data["status"] == "in_progress":
                print(f"Running: {spec_id}")
                return

        if candidates:
            print(f"Next Recommended: {candidates[0]}")
            if len(candidates) > 1:
                print(f"(Also available: {', '.join(candidates[1:4])}...)")
        else:
            print("No actionable specs found (All completed or blocked).")

    def update_status(self, spec_id: str, new_status: str):
        if spec_id not in self.status_data["specs"]:
            print(f"Error: Spec {spec_id} not found.", file=sys.stderr)
            return
        prev = self.status_data["specs"][spec_id]["status"]
        if prev == new_status:
            return

        self.status_data["specs"][spec_id]["status"] = new_status
        history_entry = {
            "from": prev,
            "to": new_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if "history" not in self.status_data["specs"][spec_id]:
            self.status_data["specs"][spec_id]["history"] = []
        self.status_data["specs"][spec_id]["history"].append(history_entry)

        self._save_status()
        print(f"Updated {spec_id}: {prev} -> {new_status}")

    def show_velocity(self):
        """Display velocity analytics and projections."""
        specs = self.status_data.get("specs", {})
        now = datetime.now(timezone.utc)

        print("\n# 📈 Velocity Analytics")
        print(f"**Generated**: {now.strftime('%Y-%m-%d %H:%M')}\n")

        # Calculate completion times
        completion_times = []
        fastest = None
        slowest = None

        for spec_id, data in specs.items():
            history = data.get("history", [])
            start_time = None
            end_time = None

            for h in history:
                if h["to"] == "in_progress" and start_time is None:
                    start_time = datetime.fromisoformat(h["timestamp"])
                if h["to"] == "completed":
                    end_time = datetime.fromisoformat(h["timestamp"])

            if start_time and end_time:
                duration = (end_time - start_time).total_seconds() / 86400  # days
                completion_times.append((spec_id, duration))

                if fastest is None or duration < fastest[1]:
                    fastest = (spec_id, duration)
                if slowest is None or duration > slowest[1]:
                    slowest = (spec_id, duration)

        print("## Completion Metrics")
        if completion_times:
            avg_time = sum(t[1] for t in completion_times) / len(completion_times)
            print(f"- **Average completion time**: {avg_time:.1f} days/SPEC")
            print(f"- **Fastest**: {fastest[0]} ({fastest[1]:.1f} days)")
            print(f"- **Slowest**: {slowest[0]} ({slowest[1]:.1f} days)")
            print(f"- **Data points**: {len(completion_times)} completed SPECs")
        else:
            print("- No completed SPECs with timing data yet.")
            avg_time = 3.0  # Default estimate
        print()

        # Weekly trend
        print("## Weekly Trend")
        weeks = {}
        for i in range(4):  # Last 4 weeks
            week_start = now - timedelta(days=(i + 1) * 7)
            week_end = now - timedelta(days=i * 7)
            week_label = f"Week -{i}" if i > 0 else "This week"
            weeks[week_label] = {"start": week_start, "end": week_end, "count": 0}

        for _data in specs.values():
            for h in _data.get("history", []):
                if h["to"] == "completed":
                    ts = datetime.fromisoformat(h["timestamp"])
                    for _week in weeks.values():
                        if _week["start"] <= ts < _week["end"]:
                            _week["count"] += 1
                            break

        for label in ["Week -3", "Week -2", "Week -1", "This week"]:
            if label in weeks:
                print(f"- **{label}**: {weeks[label]['count']} completed")
        print()

        # Projection
        print("## Projection")
        remaining = sum(
            1 for s in specs.values() if s["status"] in ["pending", "in_progress"]
        )
        in_progress = sum(1 for s in specs.values() if s["status"] == "in_progress")

        if remaining > 0 and avg_time > 0:
            estimated_days = remaining * avg_time
            estimated_date = now + timedelta(days=estimated_days)
            confidence = (
                "High"
                if len(completion_times) >= 5
                else "Medium"
                if len(completion_times) >= 2
                else "Low"
            )

            print(f"- **Remaining**: {remaining} SPECs ({in_progress} in progress)")
            print(
                f"- **Estimated completion**: {estimated_date.strftime('%Y-%m-%d')} ({estimated_days:.0f} days)"
            )
            print(
                f"- **Confidence**: {confidence} (based on {len(completion_times)} data points)"
            )
        else:
            print(f"- **Remaining**: {remaining} SPECs")
            print("- Insufficient data for projection")
        print()

        # Bottlenecks
        print("## Bottlenecks")
        bottlenecks = []
        stale_threshold = 7  # days

        for spec_id, data in specs.items():
            if data["status"] == "in_progress":
                # Find when it became in_progress
                for h in reversed(data.get("history", [])):
                    if h["to"] == "in_progress":
                        started = datetime.fromisoformat(h["timestamp"])
                        days_in_progress = (now - started).total_seconds() / 86400
                        if days_in_progress > stale_threshold:
                            bottlenecks.append((spec_id, days_in_progress))
                        break

        # Find blocked specs
        blocked = []
        for spec_id, data in specs.items():
            if data["status"] == "pending":
                for dep in data.get("dependencies", []):
                    if dep in specs and specs[dep]["status"] != "completed":
                        blocked.append((spec_id, dep))
                        break

        if bottlenecks:
            for spec_id, days in sorted(bottlenecks, key=lambda x: -x[1]):
                print(
                    f"- **{spec_id}**: In progress for {days:.0f} days (above {stale_threshold}-day threshold)"
                )

        if blocked:
            for spec_id, blocker in blocked[:5]:  # Show max 5
                print(f"- **{spec_id}**: Blocked by {blocker}")

        if not bottlenecks and not blocked:
            print("- No bottlenecks detected")


def main():
    parser = argparse.ArgumentParser(description="MoAI Orchestrator Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize spec status")
    subparsers.add_parser("status", help="Show status ASCII")
    subparsers.add_parser("next", help="Recommend next action")
    subparsers.add_parser("audit", help="Audit implementation status")
    subparsers.add_parser("git-sync", help="Sync status from git branches")
    subparsers.add_parser("report", help="Generate markdown report")
    subparsers.add_parser("velocity", help="Show velocity analytics and projections")

    up = subparsers.add_parser("update", help="Update status")
    up.add_argument("spec_id")
    up.add_argument(
        "status", choices=["pending", "in_progress", "verification", "completed"]
    )

    args = parser.parse_args()
    orch = MoAIOrchestrator()

    if args.command == "init":
        orch.init_roadmap()
    elif args.command == "status":
        orch.status_ascii()
    elif args.command == "next":
        orch.get_next_action()
    elif args.command == "audit":
        orch.audit_specs()
    elif args.command == "git-sync":
        orch.sync_git()
    elif args.command == "report":
        orch.show_report()
    elif args.command == "velocity":
        orch.show_velocity()
    elif args.command == "update":
        orch.update_status(args.spec_id, args.status)


if __name__ == "__main__":
    main()
