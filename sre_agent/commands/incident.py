import sys
from datetime import datetime, timezone
import click
from sre_agent.core.incident import (
    generate_channel_name, create_timeline,
    find_related_patterns, print_summary,
    INCIDENTS_DIR, VALID_SEVERITIES,
)


@click.command()
@click.argument("service")
@click.argument("severity", type=click.Choice(VALID_SEVERITIES, case_sensitive=False))
@click.option("--symptom", default="", help="Brief symptom description")
def incident(service: str, severity: str, symptom: str) -> None:
    """Scaffold a new incident with timeline and checklist.

    \b
    Examples:
      sre-agent incident payment-api P1
      sre-agent incident auth-service P0 --symptom "all logins failing"
    """
    severity = severity.upper()
    now = datetime.now(timezone.utc)
    channel = generate_channel_name(service, severity, now)
    incident_dir = INCIDENTS_DIR / channel

    if incident_dir.exists():
        click.echo(f"Incident directory already exists: {incident_dir}", err=True)
        sys.exit(1)

    incident_dir.mkdir(parents=True)
    timeline_path = create_timeline(incident_dir, service, severity, symptom, channel, now)
    related = find_related_patterns(service)
    print_summary(service, severity, channel, incident_dir, timeline_path, related)
