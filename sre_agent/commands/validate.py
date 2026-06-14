import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from validate_skills import validate_skill, SKILLS_DIR  # noqa: E402

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_DIM = "\033[2m"


@click.command()
@click.option("--strict", is_flag=True, help="Treat warnings as errors (for CI)")
def validate(strict: bool) -> None:
    """Validate all SKILL.md frontmatter.

    \b
    Examples:
      sre-agent validate
      sre-agent validate --strict
    """
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))

    if not skill_files:
        click.echo(f"No SKILL.md files found in {SKILLS_DIR}", err=True)
        sys.exit(1)

    results = [validate_skill(f) for f in skill_files]
    errors_total = sum(len(r.errors) for r in results)
    warnings_total = sum(len(r.warnings) for r in results)

    click.echo(f"\n{ANSI_BOLD}Skill Validator{ANSI_RESET}")
    click.echo(f"Skills scanned: {len(results)}")
    click.echo("─" * 50)

    has_failures = False
    for result in results:
        if not result.errors and not result.warnings:
            click.echo(f"  {ANSI_GREEN}✓{ANSI_RESET} {result.skill_name}")
        elif result.errors:
            has_failures = True
            click.echo(f"  {ANSI_RED}✗{ANSI_RESET} {ANSI_BOLD}{result.skill_name}{ANSI_RESET}")
            for e in result.errors:
                click.echo(f"    {ANSI_RED}ERROR:{ANSI_RESET} {e}")
            for w in result.warnings:
                click.echo(f"    {ANSI_YELLOW}WARN: {ANSI_RESET} {w}")
        else:
            if strict:
                has_failures = True
            click.echo(f"  {ANSI_YELLOW}⚠{ANSI_RESET} {result.skill_name}")
            for w in result.warnings:
                click.echo(f"    {ANSI_YELLOW}WARN: {ANSI_RESET} {w}")

    click.echo("─" * 50)

    if errors_total == 0 and warnings_total == 0:
        click.echo(f"\n{ANSI_GREEN}{ANSI_BOLD}✓ All {len(results)} skills valid{ANSI_RESET}\n")
    elif errors_total == 0:
        label = "FAIL" if strict else "PASS with warnings"
        color = ANSI_RED if strict else ANSI_YELLOW
        click.echo(f"\n{color}{ANSI_BOLD}{label}{ANSI_RESET} — {warnings_total} warning(s)\n")
    else:
        click.echo(f"\n{ANSI_RED}{ANSI_BOLD}✗ FAIL{ANSI_RESET} — {errors_total} error(s), {warnings_total} warning(s)\n")

    sys.exit(1 if has_failures else 0)
