import click

@click.group()
def cli():
    """Chat with lily: a goth chatbot"""

@cli.command('hello', help='say hello')
def hello():
    """Say hello."""
    click.echo("Hello, I'm Lily!")

if __name__ == "__main__":
    cli()