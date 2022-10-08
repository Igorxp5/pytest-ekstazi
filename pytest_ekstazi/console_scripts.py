import os
import pathlib
import argparse
import tempfile
import webbrowser

import jinja2

from .plugin import DEFAULT_CONFIG_FILE
from .config import EkstaziConfiguration

TEMPLATE_FOLDER = pathlib.Path(__file__).parent / 'resources'
MATRIX_TEMPLATE_FILENAME = 'matrix_template.html'


def ekstazi_matrix():
    parser = argparse.ArgumentParser(description='Open HTML containing the Ekstazi matrix based on the configuration file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--ekstazi-file', default=DEFAULT_CONFIG_FILE, 
        help='Ekstazi configuration file. The file contains the test cases\' file dependencies and the ' 
             'hashes of their content.'
    )

    args = parser.parse_args()

    configuration = EkstaziConfiguration(args.ekstazi_file)

    template_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_FOLDER))
    template = template_environment.get_template(MATRIX_TEMPLATE_FILENAME)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as rendered_file:
        rendered_file.write(template.render({'test_cases': configuration._dependencies.keys()}))

    webbrowser.open('file://{}'.format(rendered_file.name))
