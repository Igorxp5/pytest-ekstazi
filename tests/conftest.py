import os
import pathlib

import pytest

from pytest_ekstazi.plugin import DEFAULT_CONFIG_FILE

from .constants import TESTING_PROJECT_TEST_ROOT, CUSTOM_CONFIGURATION_FILE
from .utils import run_pytest

CONFIGURATION_FILES = [DEFAULT_CONFIG_FILE, CUSTOM_CONFIGURATION_FILE]


@pytest.fixture(autouse=True)
def delete_configuration_file():
    for configuration_file in CONFIGURATION_FILES:
        file_path = TESTING_PROJECT_TEST_ROOT / pathlib.Path(configuration_file)
        if file_path.exists():
            os.remove(file_path)
    yield
    for configuration_file in CONFIGURATION_FILES:
        file_path = TESTING_PROJECT_TEST_ROOT / pathlib.Path(configuration_file)
        if file_path.exists():
            os.remove(file_path)

@pytest.fixture(scope='session')
def project_test_cases():
    output = run_pytest(['--collect-only', '-q'])[1]
    return output.strip().split('\n')[:-2]
