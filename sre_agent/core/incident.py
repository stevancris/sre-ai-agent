#!/usr/bin/env python3
"""
Scaffold a new incident — creates a timestamped folder with timeline and checklist.

Usage:
  python scripts/incident_init.py <service> <severity>
  python scripts/incident_init.py payment-api P1
  python scripts/incident_init.py auth-service P0 --symptom "all logins failing"
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path.cwd()
INCIDENTS_DIR = REPO_ROOT / "incidents"
ONCALL_FILE = REPO_ROOT / "context" / "company" / "oncall-schedule.md"
SEVERITY_FILE = REPO_ROOT / "context" / "company" / "incident-severity.md"
KNOWLEDGE_PATTERNS = REPO_ROOT / "skills" / "knowledge-base" / "patterns"

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_CYAN = "\033[36m"
ANSI_DIM = "\033[2m"

VALID_SEVERITIES = ["P0", "P1", "P2", "P3"]

SEVERITY_COLOR = {
    "P0": ANSI_RED,
    "P1": ANSI_RED,
    "P2": ANSI_YELLOW,
    "P3": ANSI_DIM,
}

SEVERITY_EMOJI = {
    "P0": "🔴",
    "P1": "🟠",
    "P2": "🟡",
    "P3": "🟢",
}


def read_context_value(file: Path, key: str) -> str:
    """Extract a value from context markdown files."""
    if not file.exists():
        return "<not configured>"
    text = file.read_text()
    match = re.search(rf"{re.escape(key)}:\s*(.+)", text)
    if match:
        val = match.group(1).strip().strip('"').strip("'")
        return val if val and not val.startswith("<") else "<not configured>"
    return "<not configured>"


def get_severity_sla(severity: str) -> str:
    slas = {
        "P0": "Acknowledge within 5 min · Status page within 15 min",
        "P1": "Acknowledge within 15 min · Status page if >30 min",
        "P2": "Acknowledge within 30 min · No bridge required",
        "P3": "Next business day · Create ticket only",
    }
    return slas.get(severity, "")


def find_related_patterns(service: str) -> list[Path]:
    """Quick check if knowledge base has patterns for this service."""
    if not KNOWLEDGE_PATTERNS.exists():
        return []
    return [p for p in KNOWLEDGE_PATTERNS.glob("*.md") if service.lower() in p.stem.lower()]


def generate_channel_name(service: str, severity: str, now: datetime) -> str:
    date_str = now.strftime("%Y-%m-%d")
    safe_service = re.sub(r"[^a-z0-9-]", "-", service.lower()).strip("-")
    return f"inc-{date_str}-{safe_service}-{severity.lower()}"


def create_timeline(
    incident_dir: Path,
    service: str,
    severity: str,
    symptom: str,
    channel: str,
    now: datetime,
) -> Path:
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    date_str = now.strftime("%Y-%m-%d")

    oncall_primary = read_context_value(ONCALL_FILE, "primary_oncall")
    oncall_secondary = read_context_value(ONCALL_FILE, "secondary_oncall")
    slack_channel = read_context_value(ONCALL_FILE, "incident_slack_channel")
    bridge_tool = read_context_value(ONCALL_FILE, "incident_bridge_tool")
    sla = get_severity_sla(severity)

    content = f"""---
service: {service}
severity: {severity}
started: {ts}
status: active
incident-commander: {oncall_primary}
channel: {channel}
---

# Incident: {service} — {severity}
**Started:** {ts}
**Channel:** #{channel}
**Incident Commander:** {oncall_primary}
**Backup:** {oncall_secondary}

---

## Symptom

{symptom if symptom else "_Describe what is failing and how it was detected._"}

---

## Severity Checklist — {severity}

{SEVERITY_EMOJI.get(severity, "")} **SLA:** {sla}

- [ ] Alert acknowledged
- [ ] Incident channel created: #{channel}
{"- [ ] Incident bridge opened (" + bridge_tool + ")" if severity in ["P0", "P1"] else "- [ ] Bridge not required for " + severity}
{"- [ ] Engineering manager notified" if severity in ["P0", "P1"] else ""}
{"- [ ] VP Engineering notified" if severity == "P0" else ""}
{"- [ ] Status page updated" if severity in ["P0", "P1"] else ""}
- [ ] knowledge-capture run after resolution ← **mandatory**

---

## Timeline

| Time (UTC) | Who | Action |
|---|---|---|
| {now.strftime("%H:%M")} | {oncall_primary} | Incident declared — {symptom if symptom else "investigating"} |
| | | |
| | | |

---

## Investigation Notes

### What we know
_Fill as you investigate._

### What we tried
_Log each action taken and the result._

### Current theory
_Best hypothesis at this point._

---

## Resolution

**Resolved at:** _fill in_
**Root cause:** _fill in_
**Fix applied:** _fill in_
**Follow-up actions:** _link to postmortem_

---

> After resolution, run: `python scripts/knowledge_search.py "{service}"` to see if this matches a known pattern.
> Then open Claude Code and run the `knowledge-capture` skill to save what was learned.
"""

    timeline_path = incident_dir / "timeline.md"
    timeline_path.write_text(content)
    return timeline_path


def print_summary(
    service: str,
    severity: str,
    channel: str,
    incident_dir: Path,
    timeline_path: Path,
    related: list[Path],
) -> None:
    color = SEVERITY_COLOR.get(severity, ANSI_RESET)
    emoji = SEVERITY_EMOJI.get(severity, "")

    print(f"\n{ANSI_BOLD}{ANSI_GREEN}✓ Incident scaffolded{ANSI_RESET}")
    print(f"\n{ANSI_BOLD}Service:{ANSI_RESET}  {service}")
    print(f"{ANSI_BOLD}Severity:{ANSI_RESET} {color}{emoji} {severity}{ANSI_RESET} — {get_severity_sla(severity)}")
    print(f"{ANSI_BOLD}Channel:{ANSI_RESET}  #{channel}")
    print(f"{ANSI_BOLD}Files:{ANSI_RESET}")
    print(f"  {ANSI_DIM}{timeline_path}{ANSI_RESET}")

    if related:
        print(f"\n{ANSI_BOLD}{ANSI_YELLOW}⚡ Known patterns found for '{service}':{ANSI_RESET}")
        for p in related:
            print(f"  → {p.name}")
        print(f"\n  Run: {ANSI_CYAN}python scripts/knowledge_search.py \"{service}\"{ANSI_RESET}")
    else:
        print(f"\n{ANSI_DIM}No known patterns for '{service}' — first occurrence?{ANSI_RESET}")
        print(f"{ANSI_DIM}Run knowledge-capture after resolution.{ANSI_RESET}")

    print(f"\n{ANSI_BOLD}Next steps:{ANSI_RESET}")
    print(f"  1. Open #{channel} in Slack")
    print(f"  2. Fill in the timeline as you investigate")
    print(f"  3. Run knowledge-capture after resolution")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new incident",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/incident_init.py payment-api P1
  python scripts/incident_init.py auth-service P0 --symptom "all logins failing"
  python scripts/incident_init.py order-service P2 --symptom "checkout slow for EU users"
        """,
    )
    parser.add_argument("service", help="Affected service name (e.g. payment-api)")
    parser.add_argument("severity", choices=VALID_SEVERITIES, help="Severity level: P0, P1, P2, P3")
    parser.add_argument("--symptom", default="", help="Brief symptom description")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    channel = generate_channel_name(args.service, args.severity, now)
    incident_dir = INCIDENTS_DIR / channel

    if incident_dir.exists():
        print(f"{ANSI_YELLOW}⚠ Incident directory already exists: {incident_dir}{ANSI_RESET}")
        print("Delete it first or use a different service/severity combination.")
        sys.exit(1)

    incident_dir.mkdir(parents=True)

    timeline_path = create_timeline(
        incident_dir=incident_dir,
        service=args.service,
        severity=args.severity,
        symptom=args.symptom,
        channel=channel,
        now=now,
    )

    related = find_related_patterns(args.service)

    print_summary(
        service=args.service,
        severity=args.severity,
        channel=channel,
        incident_dir=incident_dir,
        timeline_path=timeline_path,
        related=related,
    )


if __name__ == "__main__":
    main()
