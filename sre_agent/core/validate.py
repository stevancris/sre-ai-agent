#!/usr/bin/env python3
"""
Validate all SKILL.md files have correct and complete frontmatter.

Usage:
  python scripts/validate_skills.py
  python scripts/validate_skills.py --strict
  python scripts/validate_skills.py --fix-dry-run

Exit codes:
  0 — all skills valid
  1 — one or more validation errors found
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SKILLS_DIR = Path.cwd() / "skills"

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_DIM = "\033[2m"
ANSI_CYAN = "\033[36m"

REQUIRED_FIELDS = ["name", "description", "allowed-tools"]
RECOMMENDED_FIELDS: list[str] = []

VALID_TOOLS = {
    "Read", "Glob", "Grep", "Write", "Edit",
    "Bash(git log:*)", "Bash(git diff:*)", "Bash(git status:*)",
    "Bash(kubectl get:*)", "Bash(kubectl describe:*)", "Bash(kubectl logs:*)",
    "Bash(terraform plan:*)", "Bash(terraform validate:*)", "Bash(terraform fmt:*)",
}

MIN_DESCRIPTION_WORDS = 20
MIN_NAME_LENGTH = 3


@dataclass
class ValidationResult:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def skill_name(self) -> str:
        return self.path.parent.name


def parse_frontmatter(text: str) -> tuple[dict, bool]:
    """Return (fields dict, has_frontmatter)."""
    if not text.strip().startswith("---"):
        return {}, False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, False
    meta = {}
    current_key = None
    current_val = []
    for line in parts[1].splitlines():
        if re.match(r"^\w[\w-]*:", line):
            if current_key:
                meta[current_key] = " ".join(current_val).strip()
            key, _, val = line.partition(":")
            current_key = key.strip()
            current_val = [val.strip().lstrip(">").strip()]
        elif line.startswith("  ") and current_key:
            current_val.append(line.strip())
    if current_key:
        meta[current_key] = " ".join(current_val).strip()
    return meta, True


def validate_skill(path: Path) -> ValidationResult:
    result = ValidationResult(path=path)
    text = path.read_text()

    meta, has_frontmatter = parse_frontmatter(text)

    if not has_frontmatter:
        result.errors.append("Missing frontmatter (file must start with ---)")
        return result

    # Required fields
    for field_name in REQUIRED_FIELDS:
        if field_name not in meta or not meta[field_name]:
            result.errors.append(f"Missing required field: '{field_name}'")

    # name matches directory
    if "name" in meta:
        expected_name = path.parent.name
        actual_name = meta["name"]
        if actual_name != expected_name:
            result.errors.append(
                f"'name' field '{actual_name}' does not match directory '{expected_name}'"
            )
        if len(actual_name) < MIN_NAME_LENGTH:
            result.errors.append(f"'name' too short: '{actual_name}'")

    # description length
    if "description" in meta and meta["description"]:
        word_count = len(meta["description"].split())
        if word_count < MIN_DESCRIPTION_WORDS:
            result.warnings.append(
                f"'description' is short ({word_count} words, recommended ≥{MIN_DESCRIPTION_WORDS})"
            )
        if "trigger keywords" not in meta["description"].lower():
            result.warnings.append("'description' has no trigger keywords — agent may not match this skill reliably")

    # allowed-tools contains only known tools
    # Tools can have spaces inside parens: Bash(kubectl get:*) — tokenize carefully
    if "allowed-tools" in meta and meta["allowed-tools"]:
        raw = meta["allowed-tools"]
        tokens = re.findall(r'Bash\([^)]+\)|\S+', raw)
        unknown = set(tokens) - VALID_TOOLS
        if unknown:
            result.warnings.append(f"Unknown tools in 'allowed-tools': {', '.join(sorted(unknown))}")

    # Recommended fields
    for rec in RECOMMENDED_FIELDS:
        if rec not in meta:
            result.warnings.append(f"Missing recommended field: '{rec}'")

    # Body must exist beyond frontmatter
    parts = text.split("---", 2)
    if len(parts) >= 3:
        body = parts[2].strip()
        if len(body) < 100:
            result.warnings.append("Skill body is very short — consider adding more instructions")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md frontmatter across all skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_skills.py           # validate all skills
  python scripts/validate_skills.py --strict  # treat warnings as errors
        """,
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (useful for CI)",
    )
    args = parser.parse_args()

    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))

    if not skill_files:
        print(f"{ANSI_RED}✗ No SKILL.md files found in {SKILLS_DIR}{ANSI_RESET}")
        sys.exit(1)

    results = [validate_skill(f) for f in skill_files]

    errors_total = sum(len(r.errors) for r in results)
    warnings_total = sum(len(r.warnings) for r in results)
    valid_count = sum(1 for r in results if r.valid)

    print(f"\n{ANSI_BOLD}SRE AI Agent — Skill Validator{ANSI_RESET}")
    print(f"Skills scanned: {len(results)}")
    print(f"{'─' * 50}")

    has_failures = False

    for result in results:
        effective_errors = result.errors + (result.warnings if args.strict else [])
        if not result.errors and not result.warnings:
            print(f"  {ANSI_GREEN}✓{ANSI_RESET} {result.skill_name}")
        elif result.errors:
            has_failures = True
            print(f"  {ANSI_RED}✗{ANSI_RESET} {ANSI_BOLD}{result.skill_name}{ANSI_RESET}")
            for e in result.errors:
                print(f"    {ANSI_RED}ERROR:{ANSI_RESET} {e}")
            for w in result.warnings:
                print(f"    {ANSI_YELLOW}WARN: {ANSI_RESET} {w}")
        else:
            if args.strict:
                has_failures = True
            print(f"  {ANSI_YELLOW}⚠{ANSI_RESET} {result.skill_name}")
            for w in result.warnings:
                print(f"    {ANSI_YELLOW}WARN: {ANSI_RESET} {w}")

    print(f"{'─' * 50}")

    if errors_total == 0 and warnings_total == 0:
        print(f"\n{ANSI_GREEN}{ANSI_BOLD}✓ All {len(results)} skills valid{ANSI_RESET}\n")
    elif errors_total == 0:
        status = ANSI_RED if args.strict else ANSI_YELLOW
        label = "FAIL" if args.strict else "PASS with warnings"
        print(f"\n{status}{ANSI_BOLD}{label}{ANSI_RESET} — {valid_count}/{len(results)} valid, {warnings_total} warning(s)")
        if args.strict:
            print(f"{ANSI_DIM}Run without --strict to treat warnings as non-blocking.{ANSI_RESET}")
        print()
    else:
        print(f"\n{ANSI_RED}{ANSI_BOLD}✗ FAIL{ANSI_RESET} — {errors_total} error(s), {warnings_total} warning(s) across {len(results)} skills\n")

    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
