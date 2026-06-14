import sys
import click
from sre_agent.core.search import load_patterns, score, print_result, PATTERNS_DIR


@click.command()
@click.argument("query")
@click.option("--service", default=None, help="Filter by service name")
@click.option("--top", default=3, show_default=True, help="Number of results to show")
def search(query: str, service: str | None, top: int) -> None:
    """Search the knowledge base for incident patterns.

    \b
    Examples:
      sre-agent search "503 errors"
      sre-agent search "connection pool" --service payment-api
      sre-agent search "memory leak" --top 1
    """
    if not PATTERNS_DIR.exists():
        click.echo(
            "No knowledge base found. Run this from inside your sre-agent directory.",
            err=True,
        )
        sys.exit(1)

    terms = query.split()
    patterns = load_patterns(service_filter=service)

    for p in patterns:
        term_score, total_score = score(p, terms)
        p.score = total_score
        p._term_score = term_score

    ranked = sorted(patterns, key=lambda p: p.score, reverse=True)
    matches = [p for p in ranked if p._term_score > 0][:top]

    click.echo(f"\nQuery: \"{query}\"")
    if service:
        click.echo(f"Service filter: {service}")
    click.echo(f"Patterns searched: {len(patterns)} · Matches: {len(matches)}")
    click.echo("─" * 60)

    if not matches:
        click.echo("\nNo matching patterns found.")
        click.echo("This may be a first occurrence — run knowledge-capture after resolution.")
        return

    for i, pattern in enumerate(matches, 1):
        print_result(pattern, i)
