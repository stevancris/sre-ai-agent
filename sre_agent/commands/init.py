import io
import re
import sys
import zipfile
from pathlib import Path

import click
import requests

REPO_ZIP = "https://github.com/stevancris/sre-ai-agent/archive/refs/heads/main.zip"
REPO_PREFIX = "sre-ai-agent-main/"

BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
CYAN  = "\033[36m"
YELLOW = "\033[33m"
WHITE = "\033[97m"

STEPS = [
    "Company info",
    "Your role",
    "Infrastructure",
    "Observability",
    "Team setup",
]


def header() -> None:
    click.echo(f"""
{BOLD}┌──────────────────────────────────────────────────┐
│            SRE AI Agent — Setup Wizard           │
│                                                  │
│  Sets up your company's institutional memory     │
│  for SRE in under 2 minutes.                     │
└──────────────────────────────────────────────────┘{RESET}
""")


def step_header(n: int, title: str) -> None:
    total = len(STEPS)
    bar = "█" * n + "░" * (total - n)
    click.echo(f"\n{CYAN}{bar}{RESET}  Step {n}/{total} — {BOLD}{title}{RESET}")
    click.echo(f"{DIM}{'─' * 52}{RESET}")


def ask_choice(prompt: str, hint: str, choices: list[str], default: str | None = None) -> str:
    click.echo(f"\n  {WHITE}{prompt}{RESET}")
    click.echo(f"  {DIM}{hint}{RESET}")
    click.echo(f"  Options: {', '.join(choices)}")
    while True:
        val = click.prompt(
            f"  {CYAN}>{RESET}",
            default=default or "",
            show_default=bool(default),
            prompt_suffix=" ",
        ).strip().lower()
        if val in [c.lower() for c in choices]:
            return val
        click.echo(f"  {YELLOW}Please choose one of: {', '.join(choices)}{RESET}")


def ask_multi(prompt: str, hint: str, choices: list[str], default: str | None = None) -> str:
    """Like ask_choice but accepts comma-separated values for multiple selections."""
    choices_lower = [c.lower() for c in choices]
    click.echo(f"\n  {WHITE}{prompt}{RESET}")
    click.echo(f"  {DIM}{hint}{RESET}")
    click.echo(f"  Options: {', '.join(choices)}")
    click.echo(f"  {DIM}You can pick multiple, e.g.: argocd, github-actions{RESET}")
    while True:
        val = click.prompt(
            f"  {CYAN}>{RESET}",
            default=default or "",
            show_default=bool(default),
            prompt_suffix=" ",
        ).strip().lower()
        parts = [p.strip() for p in val.split(",") if p.strip()]
        invalid = [p for p in parts if p not in choices_lower]
        if parts and not invalid:
            return ", ".join(parts)
        if invalid:
            click.echo(f"  {YELLOW}Unknown: {', '.join(invalid)}. Choose from: {', '.join(choices)}{RESET}")
        else:
            click.echo(f"  {YELLOW}Please enter at least one option.{RESET}")


def ask_text(prompt: str, hint: str, default: str | None = None) -> str:
    click.echo(f"\n  {WHITE}{prompt}{RESET}")
    click.echo(f"  {DIM}{hint}{RESET}")
    while True:
        val = click.prompt(
            f"  {CYAN}>{RESET}",
            default=default or "",
            show_default=bool(default),
            prompt_suffix=" ",
        ).strip()
        if val:
            return val
        click.echo(f"  {YELLOW}This field is required.{RESET}")


def gather_context() -> dict:
    # Step 1 — Company info
    step_header(1, STEPS[0])
    company = ask_text(
        "What is your company name?",
        "Used to name your agent directory and personalize outputs.",
    )

    # Step 2 — Role
    step_header(2, STEPS[1])
    role = ask_choice(
        "What is your role?",
        "This shapes how the agent communicates with you.\n"
        "  junior-sre   → step-by-step guidance, safety nets, escalation reminders\n"
        "  senior-sre   → concise, trade-offs surfaced, no hand-holding\n"
        "  sre-manager  → executive summaries, business risk framing",
        ["junior-sre", "senior-sre", "sre-manager"],
    )

    # Step 3 — Infrastructure
    step_header(3, STEPS[2])
    cloud = ask_multi(
        "What cloud providers does your team use?",
        "Tailors runbooks, kubectl commands, and cost recommendations\n"
        "  to your specific environment.\n"
        "  Multi-cloud teams can list all, e.g.: aws, gcp",
        ["aws", "gcp", "azure", "on-prem", "hybrid"],
    )
    deploy = ask_multi(
        "What deployment tools does your team use?",
        "Used in deployment safety checks and rollback guidance.\n"
        "  Most teams use more than one — list all that apply.",
        ["argocd", "flux", "github-actions", "gitlab-ci", "jenkins", "spinnaker", "other"],
    )

    # Step 4 — Observability
    step_header(4, STEPS[3])
    obs = ask_multi(
        "What observability tools does your team use?",
        "The agent references your tools when suggesting dashboards,\n"
        "  alert queries, and metric checks during incidents.\n"
        "  Many teams combine multiple tools — list all that apply.",
        ["datadog", "prometheus+grafana", "new-relic", "cloudwatch", "dynatrace", "other"],
    )

    # Step 5 — Team setup
    step_header(5, STEPS[4])
    team_size = ask_text(
        "How many SREs are on your team?",
        "Helps the agent calibrate escalation paths and on-call load.",
        default="5",
    )
    slack_channel = ask_text(
        "What are your incident Slack channels?",
        "Used in incident scaffolding and communication templates.\n"
        "  You can list multiple, e.g.: #incidents, #sre-oncall",
        default="#incidents",
    )

    return {
        "company": company,
        "role": role,
        "cloud": cloud,
        "deploy": deploy,
        "observability": obs,
        "team_size": team_size,
        "slack_channel": slack_channel,
    }


def confirm_summary(ctx: dict, target_name: str) -> bool:
    click.echo(f"\n{DIM}{'─' * 52}{RESET}")
    click.echo(f"\n{BOLD}Review your setup:{RESET}\n")
    click.echo(f"  Directory    {CYAN}{target_name}/{RESET}")
    click.echo(f"  Company      {ctx['company']}")
    click.echo(f"  Role         {ctx['role']}")
    click.echo(f"  Cloud        {ctx['cloud']}  ·  {ctx['deploy']}")
    click.echo(f"  Observability {ctx['observability']}")
    click.echo(f"  Team size    {ctx['team_size']} SREs")
    click.echo(f"  Incident channel  {ctx['slack_channel']}")
    click.echo()
    return click.confirm(f"  {CYAN}Looks good? Create the agent{RESET}", default=True)


def make_dir_name(company: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    return f"{slug}-sre-agent"


def download_template(target: Path) -> None:
    click.echo(f"\n  {DIM}Downloading latest skills from GitHub...{RESET}", nl=False)
    try:
        resp = requests.get(REPO_ZIP, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"\n\n  {YELLOW}Could not reach GitHub: {e}{RESET}", err=True)
        click.echo("  Check your internet connection and try again.", err=True)
        sys.exit(1)

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for member in zf.namelist():
            rel = member.removeprefix(REPO_PREFIX)
            if not rel or rel.startswith(".git"):
                continue
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

    click.echo(f" {GREEN}done{RESET}")


def write_context(target: Path, ctx: dict) -> None:
    context_file = target / "context" / "CONTEXT.md"
    context_file.write_text(f"""# Company Context

role: {ctx['role']}
cloud_provider: {ctx['cloud']}
observability_stack: {ctx['observability']}
deployment_tool: {ctx['deploy']}
team_size: {ctx['team_size']}
situation: learning

# Next: fill in these files to complete your setup
# - context/company/tech-stack.md      → your actual services and tools
# - context/company/oncall-schedule.md → your team members and rotation
# - context/company/incident-severity.md → your P-level definitions
""")

    oncall_file = target / "context" / "company" / "oncall-schedule.md"
    if oncall_file.exists():
        text = oncall_file.read_text().replace(
            'incident_slack_channel: "#incidents"',
            f'incident_slack_channel: "{ctx["slack_channel"]}"',
        )
        oncall_file.write_text(text)


def print_success(target: Path, ctx: dict) -> None:
    click.echo(f"""
{GREEN}{BOLD}✓ Your SRE agent is ready.{RESET}

{BOLD}What was set up:{RESET}
  19 SRE skills  ·  Knowledge base  ·  Context templates

{BOLD}Next steps:{RESET}

  {CYAN}1.{RESET}  cd {target.name}

  {CYAN}2.{RESET}  Fill in your company context:
      context/company/tech-stack.md        ← your services and tools
      context/company/oncall-schedule.md   ← your team and rotation

  {CYAN}3.{RESET}  Push to a private repo so your whole team stays in sync:
      git init && git add . && git commit -m "init sre agent"
      git remote add origin <your-private-repo-url>
      git push -u origin main

  {CYAN}4.{RESET}  Start the agent:
      claude

  {CYAN}5.{RESET}  After your first incident, run knowledge-capture
      to start building institutional memory.

{DIM}Every resolved incident that goes into knowledge-base/patterns/
makes the next one faster — for everyone on the team.{RESET}
""")


@click.command()
@click.argument("directory", required=False)
def init(directory: str | None) -> None:
    """Set up a new SRE agent for your company.

    Creates a directory with all 19 skills, context templates, and an
    empty knowledge base pre-configured for your stack.

    \b
    Examples:
      sre-agent init
      sre-agent init my-company-sre
    """
    header()
    ctx = gather_context()

    target_name = directory or make_dir_name(ctx["company"])
    target = Path.cwd() / target_name

    if not confirm_summary(ctx, target_name):
        click.echo(f"\n  {DIM}Aborted. Run sre-agent init again when ready.{RESET}\n")
        sys.exit(0)

    if target.exists():
        click.echo(f"\n  {YELLOW}'{target_name}' already exists.{RESET}")
        if not click.confirm("  Overwrite?", default=False):
            sys.exit(0)

    download_template(target)
    write_context(target, ctx)
    print_success(target, ctx)
