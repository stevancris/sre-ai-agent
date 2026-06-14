import sys
from pathlib import Path

import click

from sre_agent.core.rca_parser import parse_file, output_filename

BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
CYAN  = "\033[36m"
YELLOW = "\033[33m"
RED   = "\033[31m"

CONFIDENCE_COLOR = {"high": GREEN, "medium": YELLOW, "low": YELLOW}
CONFIDENCE_LABEL = {
    "high": "HIGH — most fields auto-extracted",
    "medium": "MEDIUM — review and fill in missing fields",
    "low": "LOW — heuristic parse only, please review all fields",
}


@click.command("import-rca")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Preview the output without saving.")
@click.option("--output-dir", default=None, type=click.Path(path_type=Path), help="Override output directory.")
def import_rca(files: tuple[Path, ...], dry_run: bool, output_dir: Path | None) -> None:
    """Convert RCA documents into knowledge-base patterns.

    Accepts our postmortem format, PagerDuty JSON, or any plain text / markdown.

    \b
    Examples:
      sre-agent import-rca postmortem-2024-11-02.md
      sre-agent import-rca incidents/*.md --dry-run
      sre-agent import-rca pagerduty-export.json
    """
    if not (Path.cwd() / "context" / "CONTEXT.md").exists():
        click.echo(f"{RED}Error: No sre-agent directory found here.{RESET}", err=True)
        click.echo("Run this command from inside your sre-agent directory.", err=True)
        click.echo("If you haven't set one up yet: sre-agent init", err=True)
        sys.exit(1)

    patterns_dir = output_dir or (Path.cwd() / "skills" / "knowledge-base" / "patterns")

    saved = 0
    skipped = 0

    for file_path in files:
        click.echo(f"\n{DIM}Processing {file_path.name}...{RESET}")

        try:
            rca, pattern_md = parse_file(file_path)
        except Exception as e:
            click.echo(f"  {RED}Error reading {file_path.name}: {e}{RESET}", err=True)
            skipped += 1
            continue

        fname = output_filename(rca)
        dest = patterns_dir / fname

        color = CONFIDENCE_COLOR[rca.confidence]
        label = CONFIDENCE_LABEL[rca.confidence]

        click.echo(f"\n  {BOLD}File:{RESET}      {file_path.name}")
        click.echo(f"  {BOLD}Format:{RESET}    {rca.source_format}")
        click.echo(f"  {BOLD}Service:{RESET}   {rca.service or DIM + 'not detected' + RESET}")
        click.echo(f"  {BOLD}Failure:{RESET}   {rca.failure_mode or DIM + 'not detected' + RESET}")
        click.echo(f"  {BOLD}MTTR:{RESET}      {rca.mttr_minutes} min" if rca.mttr_minutes else f"  {BOLD}MTTR:{RESET}      {DIM}not detected{RESET}")
        click.echo(f"  {BOLD}Confidence:{RESET} {color}{label}{RESET}")
        click.echo(f"  {BOLD}Output:{RESET}    {dest}")

        if dry_run:
            click.echo(f"\n{DIM}--- Preview ---{RESET}")
            click.echo(pattern_md[:600] + ("..." if len(pattern_md) > 600 else ""))
            click.echo(f"{DIM}--- End preview (dry-run, not saved) ---{RESET}")
            continue

        if dest.exists():
            click.echo(f"\n  {YELLOW}⚠ Pattern already exists: {dest.name}{RESET}")
            if not click.confirm("  Overwrite?", default=False):
                skipped += 1
                continue

        patterns_dir.mkdir(parents=True, exist_ok=True)
        dest.write_text(pattern_md)
        click.echo(f"\n  {GREEN}✓ Saved → {dest}{RESET}")
        saved += 1

    # Summary
    click.echo(f"\n{DIM}{'─' * 52}{RESET}")
    if dry_run:
        click.echo(f"{BOLD}Dry run complete.{RESET} Use without --dry-run to save.")
    else:
        click.echo(f"{GREEN}{BOLD}✓ {saved} pattern(s) saved.{RESET}" + (f"  {YELLOW}{skipped} skipped.{RESET}" if skipped else ""))
        if saved:
            click.echo(f"\n{DIM}Review the saved patterns and fill in any fields marked '_fill in_'.{RESET}")
            click.echo(f"{DIM}Low-confidence fields are most likely to need manual review.{RESET}\n")
