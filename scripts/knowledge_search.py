#!/usr/bin/env python3
"""
Search the SRE knowledge base for incident patterns.

Usage:
  python scripts/knowledge_search.py <query>
  python scripts/knowledge_search.py <query> --service payment-api
  python scripts/knowledge_search.py <query> --top 5
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PATTERNS_DIR = Path(__file__).parent.parent / "skills" / "knowledge-base" / "patterns"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_CYAN = "\033[36m"
ANSI_DIM = "\033[2m"


@dataclass
class Pattern:
    file: Path
    service: str
    failure_mode: str
    first_seen: str
    times_seen: int
    avg_mttr: int
    best_mttr: int
    content: str
    score: int = 0


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file."""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
            body = parts[2].strip()
    return meta, body


def load_patterns(service_filter: str | None = None) -> list[Pattern]:
    patterns = []
    for path in sorted(PATTERNS_DIR.glob("*.md")):
        text = path.read_text()
        meta, body = parse_frontmatter(text)
        service = meta.get("service", path.stem)
        if service_filter and service_filter.lower() not in service.lower():
            continue
        try:
            times_seen = int(re.sub(r"[^\d]", "", meta.get("times-seen", "0")) or 0)
            avg_mttr = int(re.sub(r"[^\d]", "", meta.get("avg-mttr-minutes", "0")) or 0)
            best_mttr = int(re.sub(r"[^\d]", "", meta.get("best-mttr-minutes", "0")) or 0)
        except ValueError:
            times_seen = avg_mttr = best_mttr = 0
        patterns.append(Pattern(
            file=path,
            service=service,
            failure_mode=meta.get("failure-mode", path.stem),
            first_seen=meta.get("first-seen", "unknown"),
            times_seen=times_seen,
            avg_mttr=avg_mttr,
            best_mttr=best_mttr,
            content=f"{path.stem} {body}",
        ))
    return patterns


STOPWORDS = {
    "the", "and", "for", "are", "this", "that", "with", "from", "have",
    "not", "was", "but", "its", "can", "will", "all", "been", "one",
    "more", "also", "into", "does", "doesnt", "exist", "random", "just",
}

def score(pattern: Pattern, terms: list[str]) -> tuple[int, int]:
    """Return (term_score, total_score). term_score must be > 0 to be a match."""
    content_lower = pattern.content.lower()
    term_score = 0
    for term in terms:
        t = term.lower()
        if len(t) < 4 or t in STOPWORDS:
            continue
        # Require whole-word match to avoid "exist" hitting "existing"
        matches = len(re.findall(rf"\b{re.escape(t)}\w{{0,3}}\b", content_lower))
        if t in pattern.service.lower() or t in pattern.failure_mode.lower():
            term_score += 5
        elif matches:
            term_score += min(matches, 10)
    boost = min(pattern.times_seen, 3)
    return term_score, term_score + boost


def extract_section(content: str, heading: str) -> str:
    """Pull out a section by its markdown heading."""
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def print_result(pattern: Pattern, rank: int) -> None:
    file_text = path_read(pattern.file)
    _, body = parse_frontmatter(file_text)

    symptom = extract_section(body, "Symptom Signature")
    fastest = extract_section(body, "Fastest Diagnostic Path")
    dead_ends = extract_section(body, "Dead Ends — Do Not Try These")

    # Trim long sections
    symptom_short = "\n".join(symptom.splitlines()[:6])
    fastest_short = "\n".join(fastest.splitlines()[:10])

    print(f"\n{ANSI_BOLD}{ANSI_CYAN}#{rank} {pattern.service} — {pattern.failure_mode.replace('-', ' ')}{ANSI_RESET}")
    print(f"{ANSI_DIM}Seen {pattern.times_seen}x · Avg MTTR {pattern.avg_mttr} min · Best {pattern.best_mttr} min · First seen {pattern.first_seen}{ANSI_RESET}")
    print(f"{ANSI_DIM}Source: {pattern.file.name}{ANSI_RESET}")

    if symptom_short:
        print(f"\n{ANSI_BOLD}Symptom Signature{ANSI_RESET}")
        print(symptom_short)

    if fastest_short:
        print(f"\n{ANSI_BOLD}Fastest Diagnostic Path{ANSI_RESET}")
        print(fastest_short)

    if dead_ends:
        first_dead_end = dead_ends.splitlines()[0]
        print(f"\n{ANSI_YELLOW}⚠ Dead ends documented — check full file before trying alternatives{ANSI_RESET}")
        print(f"{ANSI_DIM}{first_dead_end}{ANSI_RESET}")

    print(f"\n{ANSI_DIM}Full pattern: {pattern.file}{ANSI_RESET}")
    print(f"{ANSI_DIM}{'─' * 60}{ANSI_RESET}")


def path_read(p: Path) -> str:
    return p.read_text()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search SRE knowledge base patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/knowledge_search.py "503 errors"
  python scripts/knowledge_search.py "connection pool" --service payment-api
  python scripts/knowledge_search.py "memory leak" --top 3
        """,
    )
    parser.add_argument("query", help="Keywords to search for (symptoms, service name, error message)")
    parser.add_argument("--service", help="Filter by service name", default=None)
    parser.add_argument("--top", type=int, default=3, help="Number of results to show (default: 3)")
    args = parser.parse_args()

    if not PATTERNS_DIR.exists():
        print(f"{ANSI_RED}✗ Knowledge base not found: {PATTERNS_DIR}{ANSI_RESET}", file=sys.stderr)
        print("Run this script from the repo root.", file=sys.stderr)
        sys.exit(1)

    terms = args.query.split()
    patterns = load_patterns(service_filter=args.service)

    if not patterns:
        msg = f"No patterns found"
        if args.service:
            msg += f" for service '{args.service}'"
        print(f"{ANSI_YELLOW}{msg}{ANSI_RESET}")
        sys.exit(0)

    for p in patterns:
        term_score, total_score = score(p, terms)
        p.score = total_score
        p._term_score = term_score

    ranked = sorted(patterns, key=lambda p: p.score, reverse=True)
    matches = [p for p in ranked if p._term_score > 0][: args.top]

    print(f"\n{ANSI_BOLD}SRE Knowledge Base Search{ANSI_RESET}")
    print(f"Query: {ANSI_CYAN}\"{args.query}\"{ANSI_RESET}")
    if args.service:
        print(f"Service filter: {args.service}")
    print(f"Patterns searched: {len(patterns)} · Matches: {len(matches)}")
    print(f"{'─' * 60}")

    if not matches:
        print(f"\n{ANSI_YELLOW}No matching patterns found.{ANSI_RESET}")
        print("This may be a first occurrence — run knowledge-capture after resolution.")
        sys.exit(0)

    for i, pattern in enumerate(matches, 1):
        print_result(pattern, i)

    if len(patterns) - len(matches) > 0:
        unmatched = len(patterns) - len(matches)
        print(f"\n{ANSI_DIM}{unmatched} pattern(s) not shown (score: 0). Try broader keywords.{ANSI_RESET}")


if __name__ == "__main__":
    main()
