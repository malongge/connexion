import logging
import sys
from os import path

import click
from connexion import App, problem
from connexion.resolver import StubResolver

from clickclick import AliasedGroup, fatal_error


main = AliasedGroup(context_settings=dict(help_option_names=[
    '-h', '--help']))


def _operation_not_implemented():
    return problem(
        title='Not Implemented Yet',
        detail='The requested functionality is not implemented yet.',
        status=400)


def validate_wsgi_server_requirements(ctx, param, value):
    if value == 'gevent':
        try:
            import gevent.wsgi  # NOQA
        except:
            fatal_error('gevent library is not installed')
    elif value == 'tornado':
        try:
            import tornado.wsgi  # NOQA
            import tornado.httpserver  # NOQA
            import tornado.ioloop  # NOQA
        except:
            fatal_error('tornado library not installed')


@main.command()
@click.argument('spec_file')
@click.argument('base_path', required=False)
@click.option('--port', '-p', default=5000, type=int, help='Port to listen.')
@click.option('--wsgi-server', '-w', default='flask',
              type=click.Choice(['flask', 'gevent', 'tornado']),
              callback=validate_wsgi_server_requirements,
              help='Which WSGI server container to use.')
@click.option('--stub', '-s',
              help='Returns status code 400, and `Not Implemented Yet` payload, for '
              'the endpoints which handlers are not found.',
              is_flag=True, default=False)
@click.option('--hide-spec',
              help='Hides the API spec in JSON format which is by default available at `/swagger.json`.',
              is_flag=True, default=True)
@click.option('--hide-console-ui',
              help='Hides the the API console UI which is by default available at `/ui`.',
              is_flag=True, default=True)
@click.option('--console-ui-url', metavar='URL',
              help='Personalize what URL path the API console UI will be mounted.')
@click.option('--console-ui-from', metavar='PATH',
              help='Path to a customized API console UI dashboard.')
@click.option('--auth-all-paths',
              help='Enable authentication to paths not defined in the spec.',
              is_flag=True, default=False)
@click.option('--debug', '-d', help='Show debugging information.',
              is_flag=True, default=False)
def run(spec_file,
        base_path,
        port,
        wsgi_server,
        stub,
        hide_spec,
        hide_console_ui,
        console_ui_url,
        console_ui_from,
        auth_all_paths,
        debug):
    """
    Runs a server compliant with a OpenAPI/Swagger 2.0 Specification file.

    Arguments:

    - SPEC_FILE: specification file that describes the server endpoints.

    - BASE_PATH (optional): filesystem path where the API endpoints handlers are going to be imported from.
    """
    logging_level = logging.ERROR
    if debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)

    sys.path.insert(1, path.abspath(base_path or '.'))

    resolver = None
    if stub:
        resolver = StubResolver(_operation_not_implemented)

    app = App(__name__)
    app.add_api(path.abspath(spec_file), resolver=resolver)
    app.run(port=port, server=wsgi_server)
