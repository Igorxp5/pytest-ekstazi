import pathlib

import pytest

from pytest_ekstazi.plugin import DEFAULT_CONFIG_FILE

from .constants import DEFAULT_PYTEST_OPTIONS, NO_TEST_SELECTION_OPTIONS, CONFIGURATION_FILE_OPTIONS, \
    CUSTOM_FILE_NO_SELECTION_OPTIONS, TESTING_PROJECT_TEST_ROOT, XFAIL_TEST_CASES, TESTING_PROJECT_ROOT
from .utils import run_pytest, extract_pytest_results, extract_test_case_results, TestResult, edit_file_content


def test_pytest_without_ekstazi_flag():
    """
    The plugin should only be enabled when --ekstazi flag is provided. 
    No configuration file shuold be created and no test selection shuold be done.
    """
    output = run_pytest()[1]
    results = extract_pytest_results(output)

    assert TestResult.FAILED in results and TestResult.PASSED in results, 'Invalid pytest result'

    assert not (TESTING_PROJECT_TEST_ROOT / DEFAULT_CONFIG_FILE).exists(), \
        'No configuration file should be created when the plugin is not enabled'
    
    output = run_pytest()[1]
    assert results == extract_pytest_results(output), \
        'The execution should be the same if the plugin is not enabled'

    assert not (TESTING_PROJECT_TEST_ROOT / DEFAULT_CONFIG_FILE).exists(), \
        'No configuration file should be created when the plugin is not enabled'
    
    output = run_pytest(['--ekstazi'])[1]
    assert results == extract_pytest_results(output), \
        'The first execution in pytest with the plugin enabled should be the same of without the plugin enabled'
    
    assert (TESTING_PROJECT_TEST_ROOT / DEFAULT_CONFIG_FILE).exists(), \
        'Configuration file should be created when the plugin is enabled and the execution has finished'

    output = run_pytest(['--ekstazi'])[1]

    assert (TESTING_PROJECT_TEST_ROOT / DEFAULT_CONFIG_FILE).exists(), \
        'Configuration file should be created when the plugin is enabled and the execution has finished'

    results = extract_pytest_results(output)
    assert results and all(test_result in (TestResult.SKIPPED, TestResult.XFAILED) for test_result in results), \
        'The second execution in pytest with the plugin enabled shuold select no test cases (no test dependency has changed)'
    

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
def test_select_test_cases(pytest_options, project_test_cases):
    """
    The plugin should just run the test cases that have their dependencies updated.
    The other tests should be skipped.
    """
    output = run_pytest(pytest_options)[1]
    assert set(extract_test_case_results(output).keys()) == project_test_cases, 'Some test cases was not selected'
    
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'

    new_content = 'def read_qrcode(im_array):\n    return len(im_array) / 3\n\ndef read_barcode(im_array):\n    return len(im_array) / 2\n'
    with edit_file_content(pathlib.Path(TESTING_PROJECT_ROOT) / 'project' / 'readers.py', new_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        failed_tests = ['test_code_readers.py::test_read_qr_code', 'test_code_readers.py::test_read_barcode']
        assert all(results[test] == TestResult.FAILED for test in failed_tests), 'Test cases dependent of modified files did not run again'
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES if test not in failed_tests), 'Test cases was not marked as xfail'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES and test not in failed_tests), \
        'The other test cases should be marked as skipped'


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
