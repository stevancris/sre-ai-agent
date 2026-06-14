import io
import os
import re
import sys
import zipfile
from pathlib import Path

import click
import requests

REPO_ZIP = "https://github.com/stevancris/sre-ai-agent/archive/refs/heads/main.zip"
REPO_PREFIX = "sre-ai-agent-main/"

CLOUD_PROVIDERS = ["aws", "gcp", "azure", "on-prem", "hybrid"]
OBS_STACKS = ["datadog", "prometheus+grafana", "new-relic", "cloudwatch", "dynatrace", "other"]
DEPLOY_TOOLS = ["argocd", "flux", "github-actions", "gitlab-ci", "jenkins", "spinnaker", "other"]

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[32m"
ANSI_CYAN = "\033[36m"
ANSI_DIM = "\033[2m"
ANSI_YELLOW = "\033[33m"


def print_banner() -> None:
    click.echo(f"""
{ANSI_BOLD}┌─────────────────────────────────────────┐
│         SRE AI Agent — Setup Wizard     │
└─────────────────────────────────────────┘{ANSI_RESET}

This will scaffold a company-specific SRE agent in a new directory.
Takes about 2 minutes. Answer a few questions and you're ready to go.
""")


def ask(prompt: str, default: str | None = None, choices: list[str] | None = None) -> str:
    """Prompt with optional default and choice validation."""
    if choices:
        click.echo(f"\n  Options: {', '.join(choices)}")
    while True:
        value = click.prompt(
            click.style(f"  {prompt}", fg="cyan"),
            default=default or "",
            show_default=bool(default),
        ).strip()
        if not value:
            click.echo(f"  {ANSI_YELLOW}This field is required.{ANSI_RESET}")
            continue
        if choices and value.lower() not in [c.lower() for c in choices]:
            click.echo(f"  {ANSI_YELLOW}Choose one of: {', '.join(choices)}{ANSI_RESET}")
            continue
        return value.lower() if choices else value


def gather_context() -> dict:
    click.echo(f"{ANSI_BOLD}Company Context{ANSI_RESET}")
    click.echo(f"{ANSI_DIM}This information stays in your repo — never leaves your infrastructure.{ANSI_RESET}")

    company = click.prompt(click.style("  Company name", fg="cyan")).strip()
    role = ask("Your role", choices=["junior-sre", "senior-sre", "sre-manager"])
    cloud = ask("Cloud provider", choices=CLOUD_PROVIDERS)
    obs = ask("Observability stack", choices=OBS_STACKS)
    deploy = ask("Deployment tool", choices=DEPLOY_TOOLS)
    team_size = click.prompt(click.style("  Team size (number of SREs)", fg="cyan"), default="5").strip()
    slack_channel = click.prompt(click.style("  Primary incident Slack channel", fg="cyan"), default="#incidents").strip()

    return {
        "company": company,
        "role": role,
        "cloud": cloud,
        "observability": obs,
        "deploy": deploy,
        "team_size": team_size,
        "slack_channel": slack_channel,
    }


def make_dir_name(company: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    return f"{slug}-sre-agent"


def download_template(target: Path) -> None:
    click.echo(f"\n  Downloading latest skills from GitHub...")
    try:
        resp = requests.get(REPO_ZIP, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"\n  Could not reach GitHub: {e}", err=True)
        click.echo("  Check your internet connection and try again.", err=True)
        sys.exit(1)

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for member in zf.namelist():
            # Skip root-level files we don't want in the scaffolded output
            rel = member.removeprefix(REPO_PREFIX)
            if not rel or rel.startswith(".git"):
                continue
            # Exclude package source, pyproject, scripts (user gets CLI instead)
            if rel.startswith(("sre_agent/", "scripts/", "incidents/")):
                continue
            if rel in ("pyproject.toml", "ROADMAP.md"):
                continue

            dest = target / rel
            if member.endswith("/"):
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(member))


def write_context(target: Path, ctx: dict) -> None:
    context_file = target / "context" / "CONTEXT.md"
    content = f"""# Company Context

role: {ctx['role']}
cloud_provider: {ctx['cloud']}
observability_stack: {ctx['observability']}
deployment_tool: {ctx['deploy']}
team_size: {ctx['team_size']}
situation: learning

# Fill in the files below to complete your setup:
# - context/company/tech-stack.md    → your actual tools and services
# - context/company/oncall-schedule.md → your team and rotation
# - context/company/incident-severity.md → your P-level definitions
"""
    context_file.write_text(content)

    oncall_file = target / "context" / "company" / "oncall-schedule.md"
    oncall_text = oncall_file.read_text()
    oncall_text = oncall_text.replace(
        'incident_slack_channel: "#incidents"',
        f'incident_slack_channel: "{ctx["slack_channel"]}"',
    )
    oncall_file.write_text(oncall_text)


def print_success(target: Path, ctx: dict) -> None:
    click.echo(f"""
{ANSI_BOLD}{ANSI_GREEN}✓ Done! Your SRE agent is ready.{ANSI_RESET}

  {ANSI_BOLD}Directory:{ANSI_RESET} {target}
  {ANSI_BOLD}Company:{ANSI_RESET}   {ctx['company']}
  {ANSI_BOLD}Stack:{ANSI_RESET}     {ctx['cloud']} · {ctx['observability']} · {ctx['deploy']}

{ANSI_BOLD}Next steps:{ANSI_RESET}

  {ANSI_CYAN}1.{ANSI_RESET} cd {target.name}
  {ANSI_CYAN}2.{ANSI_RESET} Fill in context/company/tech-stack.md with your actual services
  {ANSI_CYAN}3.{ANSI_RESET} Run: claude

{ANSI_DIM}Your knowledge base starts empty — it grows from your own incidents.
After each incident, run the knowledge-capture skill to save what was learned.{ANSI_RESET}
""")


@click.command()
@click.argument("directory", required=False)
def init(directory: str | None) -> None:
    """Set up a new SRE agent for your company.

    Creates a directory with all skills, context templates, and knowledge base
    pre-configured for your stack. Run 'claude' inside it to get started.

    \b
    Examples:
      sre-agent init
      sre-agent init my-company-sre
    """
    print_banner()
    ctx = gather_context()

    target_name = directory or make_dir_name(ctx["company"])
    target = Path.cwd() / target_name

    if target.exists():
        click.echo(f"\n  {ANSI_YELLOW}Directory '{target_name}' already exists.{ANSI_RESET}")
        if not click.confirm("  Overwrite?", default=False):
            click.echo("  Aborted.")
            sys.exit(0)

    download_template(target)
    write_context(target, ctx)
    print_success(target, ctx)
