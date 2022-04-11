import pytest

from constants import DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS, CONFIGURATION_FILE_OPTIONS, \
    CUSTOM_FILE_NO_SELECTION_OPTIONS


def test_pytest_without_ekstazi_flag():
    """
    The plugin should only be enabled when --ekstazi flag is provided. 
    No configuration file shuold be created and no test selection shuold be done.
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS,
                                            CONFIGURATION_FILE_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_save_test_dependencies(pytest_options):
    """
    The plugin should save each test dependencies in the configuration file at end of the test sesssion
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS,
                                            CONFIGURATION_FILE_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_save_test_dependencies_hashes(pytest_options):
    """
    The plugin should save each test dependencies hashes in the configuration file 
    at end of the test sesssion
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS,
                                            CONFIGURATION_FILE_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_save_test_hashes(pytest_options):
    """
    The plugin should save each test hash in the configuration file at end of the test sesssion
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS,
                                            CONFIGURATION_FILE_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_save_test_results(pytest_options):
    """
    The plugin should save the result of each test (PASS, FAIL, SKIPPED) in the configuration file 
    at end of the test sesssion
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_test_cases(pytest_options):
    """
    The plugin should just run the test cases that have their dependencies updated.
    The other tests should be skipped.
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_changed_test_cases(pytest_options):
    """The plugin should select test cases that had its steps changed."""
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_arguments_changed_test_cases(pytest_options):
    """The plugin should select test cases that had its arguments (fixture) changed."""
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_fixture_steps_changed_test_cases(pytest_options):
    """The plugin should select test cases that had the steps of its fixtures changed."""
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_xfail_cached_failed_test_cases(pytest_options):
    """
    The plugin shuold mark as xfail test cases would be skipped due no dependency changes or test itself 
    or fixture changes, but it has failed in previous execution.
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [NO_TEST_SELECTION_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_no_ekstazi_selection_option(pytest_options):
    """
    The plugin should not skip any test case by using Ekstazi selection algorithm when 
    --no-ekstazi-selection flag is provided.
    """
    raise NotImplementedError

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS,
                                            CONFIGURATION_FILE_OPTIONS, CUSTOM_FILE_NO_SELECTION_OPTIONS])
def test_save_new_test_dependency(pytest_options):
    """
    The plugin should save new test dependencies when the test case had that kind of changing.
    """
    raise NotImplementedError
