import sys
import click
from api.api import AnkiStepAPI

def get_api():
    try:
        return AnkiStepAPI()
    except Exception:
        click.secho("Check Anki is running with AnkiConnect plugin!", fg="red", bold=True, err=True)
        sys.exit(1)

def error_and_exit(mes):
    click.secho(mes, fg="red", bold=True, err=True)
    sys.exit(1)

@click.group()
def cli():
    pass


@cli.command()
@click.argument('client_id')
@click.argument('client_secret')
def auth(client_id, client_secret):
    """
    Authorize in Stepik with given client credentials.\n
    Format: auth <client_id> <client_secret>\n
    """

    api = get_api()
    try:
        api.authorize(client_id, client_secret)
    except ConnectionError as e:
        error_and_exit(*e.args)
    click.echo("You successfully authorize!")

@cli.command()
@click.argument('course_id')
def convert(course_id):
    """
    Convert course to Anki notes.\n
    Format: convert <course_id>\n
    """
    api = get_api()
    try:
        api.load_stepik_course(course_id)
    except ConnectionError as e:
        error_and_exit(*e.args)
    click.echo("Save course to Anki...")
    api.save_quizes_anki()
    click.echo("Converting was completed successfully!")


        


if __name__ == "__main__":
    cli()
