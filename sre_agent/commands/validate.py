import sys
import click
from sre_agent.core.validate import validate_skill, SKILLS_DIR

BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


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
        click.echo(f"No SKILL.md files found in {SKILLS_DIR}. Run from inside your sre-agent directory.", err=True)
        sys.exit(1)

    results = [validate_skill(f) for f in skill_files]
    errors_total = sum(len(r.errors) for r in results)
    warnings_total = sum(len(r.warnings) for r in results)

    click.echo(f"\n{BOLD}Skill Validator{RESET} — {len(results)} skills")
    click.echo("─" * 50)

    has_failures = False
    for result in results:
        if not result.errors and not result.warnings:
            click.echo(f"  {GREEN}✓{RESET} {result.skill_name}")
        elif result.errors:
            has_failures = True
            click.echo(f"  {RED}✗{RESET} {BOLD}{result.skill_name}{RESET}")
            for e in result.errors:
                click.echo(f"    {RED}ERROR:{RESET} {e}")
            for w in result.warnings:
                click.echo(f"    {YELLOW}WARN:{RESET}  {w}")
        else:
            if strict:
                has_failures = True
            click.echo(f"  {YELLOW}⚠{RESET} {result.skill_name}")
            for w in result.warnings:
                click.echo(f"    {YELLOW}WARN:{RESET}  {w}")

    click.echo("─" * 50)

    if errors_total == 0 and warnings_total == 0:
        click.echo(f"\n{GREEN}{BOLD}✓ All {len(results)} skills valid{RESET}\n")
    elif errors_total == 0:
        label = "FAIL" if strict else "PASS with warnings"
        color = RED if strict else YELLOW
        click.echo(f"\n{color}{BOLD}{label}{RESET} — {warnings_total} warning(s)\n")
    else:
        click.echo(f"\n{RED}{BOLD}✗ FAIL{RESET} — {errors_total} error(s), {warnings_total} warning(s)\n")

    sys.exit(1 if has_failures else 0)
