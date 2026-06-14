"""
Parse RCA documents from various formats into knowledge-base pattern format.

Supported formats:
  - SRE AI Agent postmortem (our own markdown format)
  - PagerDuty JSON export
  - Generic markdown / plain text (heuristic fallback)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


Format = Literal["postmortem", "pagerduty", "generic"]


@dataclass
class ParsedRCA:
    service: str = ""
    failure_mode: str = ""
    first_seen: str = ""
    last_seen: str = ""
    mttr_minutes: int = 0
    symptoms: list[str] = field(default_factory=list)
    trigger: str = ""
    root_cause: str = ""
    resolution: str = ""
    dead_ends: list[str] = field(default_factory=list)
    prevention: list[str] = field(default_factory=list)
    notes: str = ""
    source_format: Format = "generic"
    confidence: Literal["high", "medium", "low"] = "low"


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

def detect_format(content: str) -> Format:
    """Detect RCA format from content."""
    stripped = content.strip()

    # PagerDuty JSON
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            data = json.loads(stripped)
            if isinstance(data, dict) and any(
                k in data for k in ("incident", "postmortem", "title", "id")
            ):
                return "pagerduty"
        except json.JSONDecodeError:
            pass

    # Our own postmortem format — has specific section headers
    postmortem_markers = [
        "## Timeline",
        "## Root Cause Analysis",
        "## Contributing Factor",
        "## Action Items",
        "**[STARTED]**",
        "**[RESOLVED]**",
        "**MTTR:**",
    ]
    if sum(1 for m in postmortem_markers if m in content) >= 2:
        return "postmortem"

    return "generic"


# ---------------------------------------------------------------------------
# Our own postmortem format parser
# ---------------------------------------------------------------------------

def parse_postmortem(content: str) -> ParsedRCA:
    """Parse SRE AI Agent postmortem markdown format."""
    rca = ParsedRCA(source_format="postmortem")

    # Service name — from title "# Postmortem: <service>" or "# <service> —"
    title_match = re.search(r"^#\s+(?:Postmortem[:\s—]+)?(.+?)(?:\s*—|\s*\||\n)", content, re.MULTILINE)
    if title_match:
        rca.service = _slugify(title_match.group(1).strip())

    # Dates from timeline markers
    started = re.search(r"\*\*\[STARTED\]\*\*.*?(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})", content)
    resolved = re.search(r"\*\*\[RESOLVED\]\*\*.*?(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})", content)
    if started:
        rca.first_seen = _normalize_date(started.group(1))
        rca.last_seen = rca.first_seen
    if resolved:
        rca.last_seen = _normalize_date(resolved.group(1))

    # MTTR
    mttr_match = re.search(r"\*\*MTTR[:\*\s]+(\d+)\s*(min|hour|hr)", content, re.IGNORECASE)
    if mttr_match:
        val = int(mttr_match.group(1))
        unit = mttr_match.group(2).lower()
        rca.mttr_minutes = val * 60 if unit in ("hour", "hr") else val

    # Root cause — from five-whys or "Root Cause:" line
    rc_match = re.search(
        r"Root Cause\s*:(.+?)(?:\n\n|\Z)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if rc_match:
        rca.root_cause = rc_match.group(1).strip()[:500]

    # Impact / symptoms — from "## Impact" or "## Symptom" section
    symptoms_match = _extract_section(content, ["Impact", "Symptom", "Summary"])
    if symptoms_match:
        rca.symptoms = _extract_bullets(symptoms_match)

    # Resolution — from "## Resolution" section
    resolution_match = _extract_section(content, ["Resolution", "Mitigation", "Fix"])
    if resolution_match:
        rca.resolution = resolution_match.strip()[:800]

    # Action items → prevention
    actions_match = _extract_section(content, ["Action Items", "Follow-up", "Prevention"])
    if actions_match:
        rca.prevention = _extract_bullets(actions_match)

    # Failure mode from root cause or title
    rca.failure_mode = _derive_failure_mode(rca.root_cause or symptoms_match or "")

    rca.confidence = "high" if (rca.service and rca.root_cause and rca.resolution) else "medium"
    return rca


# ---------------------------------------------------------------------------
# PagerDuty JSON parser
# ---------------------------------------------------------------------------

def parse_pagerduty(content: str) -> ParsedRCA:
    """Parse PagerDuty incident/postmortem JSON export."""
    rca = ParsedRCA(source_format="pagerduty")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return rca

    # PagerDuty wraps in {"incident": {...}} or {"postmortem": {...}}
    inc = data.get("incident") or data.get("postmortem") or data

    # Service
    service_name = (
        inc.get("service", {}).get("summary")
        or inc.get("service_name")
        or inc.get("title", "")
    )
    rca.service = _slugify(service_name)

    # Dates — preserve raw strings for MTTR, then normalize to YYYY-MM-DD
    raw_start = inc.get("created_at", "") or inc.get("started_at", "")
    raw_end = inc.get("resolved_at", "")
    rca.first_seen = _normalize_date(raw_start)
    rca.last_seen = _normalize_date(raw_end) or rca.first_seen

    # MTTR — use raw ISO strings for accurate minute calculation
    if raw_start and raw_end:
        try:
            start = datetime.fromisoformat(raw_start.rstrip("Z").split("+")[0])
            end = datetime.fromisoformat(raw_end.rstrip("Z").split("+")[0])
            rca.mttr_minutes = max(0, int((end - start).total_seconds() / 60))
        except ValueError:
            pass

    # Description / symptoms
    description = inc.get("description") or inc.get("summary") or ""
    if description:
        rca.symptoms = [description.strip()]

    # Postmortem body (if present)
    body = inc.get("body", {}).get("content") or inc.get("postmortem_body") or ""
    if body:
        rc_match = re.search(r"root cause[:\s]+(.+?)(?:\n\n|\Z)", body, re.IGNORECASE | re.DOTALL)
        if rc_match:
            rca.root_cause = rc_match.group(1).strip()[:500]

    rca.failure_mode = _derive_failure_mode(rca.root_cause or description)
    rca.confidence = "high" if (rca.service and rca.first_seen) else "medium"
    return rca


# ---------------------------------------------------------------------------
# Generic heuristic parser (fallback)
# ---------------------------------------------------------------------------

def parse_generic(content: str) -> ParsedRCA:
    """Heuristic parser for unstructured RCA text."""
    rca = ParsedRCA(source_format="generic")

    # Service name — look for common patterns
    service_patterns = [
        r"service[:\s]+([a-z0-9][a-z0-9_-]+)",
        r"component[:\s]+([a-z0-9][a-z0-9_-]+)",
        r"system[:\s]+([a-z0-9][a-z0-9_-]+)",
        r"app(?:lication)?[:\s]+([a-z0-9][a-z0-9_-]+)",
        r"([a-z0-9][a-z0-9_-]+-(?:api|service|worker|svc|app))\b",
    ]
    for pat in service_patterns:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            rca.service = _slugify(m.group(1))
            break

    # Dates
    date_matches = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", content)
    if date_matches:
        rca.first_seen = date_matches[0]
        rca.last_seen = date_matches[-1] if len(date_matches) > 1 else date_matches[0]

    # MTTR
    mttr_match = re.search(r"(?:mttr|resolved in|duration)[:\s]+(\d+)\s*(min|hour|hr|h\b)", content, re.IGNORECASE)
    if mttr_match:
        val = int(mttr_match.group(1))
        unit = mttr_match.group(2).lower()
        rca.mttr_minutes = val * 60 if unit in ("hour", "hr", "h") else val

    # Root cause
    rc_patterns = [
        r"root cause\s*:(.+?)(?:\n\n|\Z)",
        r"caused by\s*:(.+?)(?:\n|\Z)",
        r"reason\s*:(.+?)(?:\n|\Z)",
    ]
    for pat in rc_patterns:
        m = re.search(pat, content, re.IGNORECASE | re.DOTALL)
        if m:
            rca.root_cause = m.group(1).strip()[:500]
            break

    # Symptoms — lines with error/alert keywords
    symptom_lines = [
        line.strip() for line in content.splitlines()
        if re.search(r"\b(error|fail|down|outage|alert|503|500|timeout|crash)\b", line, re.IGNORECASE)
        and len(line.strip()) > 20
    ]
    rca.symptoms = symptom_lines[:5]

    # Resolution
    res_match = re.search(r"(?:fix|resolution|resolved by|solution)[:\s]+(.+?)(?:\n\n|\Z)", content, re.IGNORECASE | re.DOTALL)
    if res_match:
        rca.resolution = res_match.group(1).strip()[:800]

    rca.failure_mode = _derive_failure_mode(rca.root_cause or " ".join(rca.symptoms))
    rca.confidence = "low"
    return rca


# ---------------------------------------------------------------------------
# Convert ParsedRCA → knowledge-base pattern markdown
# ---------------------------------------------------------------------------

def to_pattern(rca: ParsedRCA) -> str:
    """Render a ParsedRCA into knowledge-base pattern markdown format."""
    today = datetime.now().strftime("%Y-%m-%d")
    service = rca.service or "unknown-service"
    failure_mode = rca.failure_mode or "unknown-failure"
    first_seen = rca.first_seen or today
    last_seen = rca.last_seen or today
    mttr = f"{rca.mttr_minutes} min" if rca.mttr_minutes else "_fill in_"

    symptoms_block = "\n".join(f"- {s}" for s in rca.symptoms) if rca.symptoms else "- _fill in_"
    dead_ends_block = "\n".join(f"- {d}" for d in rca.dead_ends) if rca.dead_ends else "- _fill in_"
    prevention_block = "\n".join(f"- [ ] {p}" for p in rca.prevention) if rca.prevention else "- [ ] _fill in_"

    confidence_note = {
        "high": "<!-- Confidence: HIGH — most fields auto-extracted -->",
        "medium": "<!-- Confidence: MEDIUM — review and fill in missing fields -->",
        "low": "<!-- Confidence: LOW — heuristic parse only, please review all fields -->",
    }[rca.confidence]

    return f"""---
service: {service}
failure-mode: {failure_mode}
first-seen: {first_seen}
times-seen: 1
last-seen: {last_seen}
avg-mttr-minutes: {rca.mttr_minutes or 0}
best-mttr-minutes: {rca.mttr_minutes or 0}
related-incidents: []
---

{confidence_note}

# Failure Pattern: {service} — {failure_mode.replace("-", " ").title()}

## Symptom Signature

How to recognize this pattern within the first 2 minutes:

{symptoms_block}

## Trigger Conditions

{rca.trigger or "_fill in — what usually causes this failure mode_"}

## Fastest Diagnostic Path

1. _fill in — fastest command or check to confirm this pattern_
2. _fill in — how to confirm the trigger_

Total time to confirm: ~_X_ minutes

## Resolution

{rca.resolution or "_fill in_"}

## Why It Happens

{rca.root_cause or "_fill in_"}

## Prevention

{prevention_block}

## Dead Ends — Do Not Try These

{dead_ends_block}

## Notes

{rca.notes or "_fill in any additional context, edge cases, or variations_"}
"""


# ---------------------------------------------------------------------------
# File-level entry point
# ---------------------------------------------------------------------------

def parse_file(path: Path) -> tuple[ParsedRCA, str]:
    """Parse an RCA file. Returns (ParsedRCA, pattern_markdown)."""
    content = path.read_text(encoding="utf-8", errors="replace")
    fmt = detect_format(content)

    if fmt == "postmortem":
        rca = parse_postmortem(content)
    elif fmt == "pagerduty":
        rca = parse_pagerduty(content)
    else:
        rca = parse_generic(content)

    pattern = to_pattern(rca)
    return rca, pattern


def output_filename(rca: ParsedRCA) -> str:
    service = rca.service or "unknown-service"
    failure_mode = rca.failure_mode or "unknown-failure"
    return f"{service}-{failure_mode}.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_section(content: str, headings: list[str]) -> str:
    """Extract content under the first matching markdown heading."""
    pattern = r"(?:^|\n)#{1,3}\s+(?:" + "|".join(re.escape(h) for h in headings) + r")\s*\n(.*?)(?=\n#{1,3}\s|\Z)"
    m = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_bullets(text: str) -> list[str]:
    """Extract bullet points from a markdown section."""
    bullets = re.findall(r"^[-*]\s+(.+)$", text, re.MULTILINE)
    if bullets:
        return [b.strip() for b in bullets[:10]]
    # Fallback: non-empty lines
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    return lines[:5]


def _normalize_date(raw: str) -> str:
    """Try to return YYYY-MM-DD from various date strings."""
    if not raw:
        return ""
    # Already ISO format
    iso = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    if iso:
        return iso.group(1)
    # Try parsing ISO datetime
    try:
        return datetime.fromisoformat(raw.rstrip("Z").split("+")[0]).strftime("%Y-%m-%d")
    except ValueError:
        pass
    return ""


def _slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text.strip())
    return re.sub(r"-+", "-", text).strip("-")[:50]


def _derive_failure_mode(text: str) -> str:
    """Guess a failure-mode slug from root cause or symptom text."""
    if not text:
        return "unknown-failure"
    # Map common keywords to slug
    keywords = {
        r"connection.pool|pool.exhaust": "connection-pool-exhaustion",
        r"memory.leak|oom|out.of.memory": "memory-leak",
        r"maxmemory|evict|redis.memory|session.evict": "redis-memory-exhaustion",
        r"cpu.throttl|high.cpu": "cpu-throttling",
        r"disk.full|disk.space|storage": "disk-full",
        r"timeout|timed.out": "timeout",
        r"deploy|rollout|regression": "deploy-regression",
        r"dns|resolution.fail": "dns-failure",
        r"certif|tls|ssl|expir": "certificate-expiry",
        r"rate.limit|throttl": "rate-limiting",
        r"cascade|domino|ripple": "cascading-failure",
        r"deadlock|lock.wait": "database-deadlock",
        r"crash.loop|crashloop": "crash-loop",
        r"oom.kill|out.of.memory": "oom-kill",
        r"network.partition|split.brain": "network-partition",
        r"config.change|misconfigur": "misconfiguration",
    }
    text_lower = text.lower()
    for pat, slug in keywords.items():
        if re.search(pat, text_lower):
            return slug
    # Fallback: use first 3 meaningful words
    words = re.findall(r"[a-z]+", text_lower)
    stopwords = {
        "the", "a", "an", "in", "on", "at", "to", "of", "and", "or", "was",
        "is", "by", "due", "set", "its", "not", "for", "are", "be", "been",
        "this", "that", "with", "from", "causing", "caused", "reached",
        "resolved", "utc", "started", "detected", "acknowledged",
    }
    meaningful = [w for w in words if w not in stopwords and len(w) > 3][:3]
    return "-".join(meaningful) if meaningful else "unknown-failure"
