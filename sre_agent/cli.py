import click
from sre_agent import __version__
from sre_agent.commands.init import init
from sre_agent.commands.search import search
from sre_agent.commands.incident import incident
from sre_agent.commands.validate import validate
from sre_agent.commands.import_rca import import_rca


@click.group()
@click.version_option(__version__, prog_name="sre-agent")
def cli():
    """SRE AI Agent — your company's institutional memory for SRE.

    Get started:

    \b
      sre-agent init            Set up a new SRE agent for your company
      sre-agent search QUERY    Search the knowledge base
      sre-agent incident        Scaffold a new incident
      sre-agent validate        Validate all SKILL.md files
      sre-agent import-rca      Convert RCA documents into knowledge-base patterns
    """


cli.add_command(init)
cli.add_command(search)
cli.add_command(incident)
cli.add_command(validate)
cli.add_command(import_rca)
