import pathlib

CUSTOM_CONFIGURATION_FILE = 'custom_ekstazi.json'
DEFAULT_PYTEST_OPTIONS = ['--ekstazi']
NO_TEST_SELECTION_OPTIONS = DEFAULT_PYTEST_OPTIONS + ['--no-test-selection']
CONFIGURATION_FILE_OPTIONS = DEFAULT_PYTEST_OPTIONS + ['--ekstazi-file', CUSTOM_CONFIGURATION_FILE]
CUSTOM_FILE_NO_SELECTION_OPTIONS = DEFAULT_PYTEST_OPTIONS + ['--no-test-selection', '--ekstazi-file', 
                                                             CUSTOM_CONFIGURATION_FILE]

TESTING_PROJECT_ROOT = pathlib.Path(__file__).parent / 'project'