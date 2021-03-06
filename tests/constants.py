import pathlib

CUSTOM_CONFIGURATION_FILE = 'custom_ekstazi.json'
DEFAULT_PYTEST_OPTIONS = ['--ekstazi']
CONFIGURATION_FILE_OPTIONS = DEFAULT_PYTEST_OPTIONS + ['--ekstazi-file', CUSTOM_CONFIGURATION_FILE]

TESTING_PROJECT_ROOT = pathlib.Path(__file__).parent / 'project'
TESTING_PROJECT_TEST_ROOT = TESTING_PROJECT_ROOT / 'tests'

XFAIL_TEST_CASES = ['test_assert.py::test_assert_false', 'test_code_readers.py::test_read_barcode']
