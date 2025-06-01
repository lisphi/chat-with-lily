import click

@click.group()
def cli():
    """Chat with lily: a goth chatbot"""

@cli.command('hello', help='say hello')
def hello():
    """Say hello."""
    click.echo("Hello, I'm Lily!")

@cli.command("make-dataset", help="generate qa messages")
def qa_generator():
    from lily.data.qa_gen import DataProcessor
    processor = DataProcessor()
    processor.process()

@cli.command("calc-cutoff-length", help="calculate cutoff length of qa messages")
def calc_length_cdf():
    from lily.utils.length_cdf import length_cdf
    length_cdf()

if __name__ == "__main__":
    cli()