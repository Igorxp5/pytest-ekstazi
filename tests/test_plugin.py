import pathlib

import pytest

from pytest_ekstazi.plugin import DEFAULT_CONFIG_FILE
from pytest_ekstazi.config import EkstaziConfiguration

from .constants import CUSTOM_CONFIGURATION_FILE, DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS, \
    TESTING_PROJECT_TEST_ROOT, XFAIL_TEST_CASES, TESTING_PROJECT_ROOT
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
    

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_dependencies(pytest_options, project_test_cases):
    """
    The plugin should save each test dependencies in the configuration file at end of the test sesssion
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_dependencies = {
        'test_code_readers.py::test_read_qr_code': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py')
        ],
        'test_code_readers.py::test_read_barcode': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py')
        ],
        'test_product.py::test_product_access_level': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'access_level.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'product.py')
        ],
        'test_product.py::test_delete_product': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'product.py')
        ],
        'test_product.py::test_insert_product': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'product.py')
        ],
        'test_product.py::test_unauthorized_access': [
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'product.py'),
            str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'user.py')
        ]
    }
    configuration = EkstaziConfiguration(configuration_file)
    for test_case in expected_test_dependencies:
        test_file, test_name = test_case.split('::', 1)
        test_file = TESTING_PROJECT_ROOT / 'tests' / test_file
        test_dependencies = configuration.get_test_dependencies(test_file, test_name)
        assert set(expected_test_dependencies[test_case]) == set(test_dependencies), \
            f'The test dependencies of "{test_case}" are not right'


@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_dependencies_hashes(pytest_options, project_test_cases):
    """
    The plugin should save each test dependencies hashes in the configuration file 
    at end of the test sesssion and when the test dependency change the hash of the file should change too. 
    """
    
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_dependencies_hashes = {
        str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py'): '9baeb77b1dde08611b7bcc494740a0d761b7bcb2',
        str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'access_level.py'): 'e6dbe82d708fa2a0e887dfb05cce72ece5d3f03c',
        str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py'): '3822ed5dddaa1ea8e4559fc59cb46df61e7a4db0',
        str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'product.py'): 'ace7f5c2de1963b01d91da0ee1f123b7abffe5c9',
        str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'user.py'): '08912fdfad5bff533e6a17bc522797a76fae5fd6'
    }

    configuration = EkstaziConfiguration(configuration_file)
    for dependency_file in expected_test_dependencies_hashes:
        dependency_hash = configuration.get_dependency_hash(dependency_file)
        assert expected_test_dependencies_hashes[dependency_file] == dependency_hash, \
            f'The test dependencies hashes of "{dependency_file}" are not right'
    
    test_code_readers = TESTING_PROJECT_ROOT / 'project' / 'readers.py'
    test_code_readers_content = ''
    with open(test_code_readers) as file:
        test_code_readers_content = file.readlines()
    
    # Edit line 1
    test_code_readers_content[0] ='from .database import Database\n' +  test_code_readers_content[0]
   
    edited_test_code_readers_content = ''.join(test_code_readers_content)

    with edit_file_content(test_code_readers, edited_test_code_readers_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        used_test_case = 'test_code_readers.py::test_read_qr_code'
        failed_test_cases = ['test_code_readers.py::test_read_barcode']
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(used_test_case)
        for xfail_test_case in XFAIL_TEST_CASES:
            skipped_test_cases.remove(xfail_test_case)
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES if test not in failed_test_cases), 'Test cases dependent of modified files did not run again'
        assert all(results[test] == TestResult.FAILED for test in failed_test_cases), 'Test cases dependent of modified files did not failed again'
        assert results[used_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'

    configuration = EkstaziConfiguration(configuration_file)
    
    dependency_file = str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py')
    dependency_hash = configuration.get_dependency_hash(dependency_file)
    assert dependency_hash == '2e75388373cf24f8a62f9ee1518bae0f9912ac69', \
        f'The test dependencies hashes of "{dependency_file}" are not right'


@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_hashes(pytest_options, project_test_cases):
    """
    The plugin should save each test hash in the configuration file at end of the test sesssion. The hash of a test case is
    the hash of whole file + its content. 
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_hashes = {
        'test_assert.py::test_assert_false': '9d9b0600bb562b97148debeb8335f94f365380c3',
        'test_assert.py::test_assert_passed': 'bd36527867ab74ebf6c5425a5e337fdaaee22078',
        'test_code_readers.py::test_read_qr_code': '2c18c1bc2b1cead94a664cfa1a5e0996efc79b4f',
        'test_code_readers.py::test_read_barcode': '6ef94e6263e3db18f4c2a6fd79c1314eb06e75c2',
        'test_product.py::test_product_access_level': '286591afcdf99594b07d89861ffa189f8195b265',
        'test_product.py::test_delete_product': 'db3636144e35d2a4b52f3d059bf56df324b848aa',
        'test_product.py::test_insert_product': 'ec454c82648d1ebbf8ecddbff0ceea6492a815aa',
        'test_product.py::test_unauthorized_access': '57f6a1a7d13628228209553abd5458898b369388'
    }

    configuration = EkstaziConfiguration(configuration_file)
    for test_case in expected_test_hashes:
        test_file, test_name = test_case.split('::', 1)
        test_file = TESTING_PROJECT_ROOT / 'tests' / test_file
        test_hash = configuration.get_test_hash(test_file.name, test_name)
        assert expected_test_hashes[test_case] == test_hash, \
            f'The test hash of "{test_file.name}" are not right'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_hashes_changes(pytest_options, project_test_cases):
    """
    The plugin should save each test hash in the configuration file at end of the test sesssion
    and when the test file changes the hash of the file should change too.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_hashes = {
        'test_assert.py::test_assert_false': '9d9b0600bb562b97148debeb8335f94f365380c3',
        'test_assert.py::test_assert_passed': 'bd36527867ab74ebf6c5425a5e337fdaaee22078',
        'test_code_readers.py::test_read_qr_code': '2c18c1bc2b1cead94a664cfa1a5e0996efc79b4f',
        'test_code_readers.py::test_read_barcode': '6ef94e6263e3db18f4c2a6fd79c1314eb06e75c2',
        'test_product.py::test_product_access_level': '286591afcdf99594b07d89861ffa189f8195b265',
        'test_product.py::test_delete_product': 'db3636144e35d2a4b52f3d059bf56df324b848aa',
        'test_product.py::test_insert_product': 'ec454c82648d1ebbf8ecddbff0ceea6492a815aa',
        'test_product.py::test_unauthorized_access': '57f6a1a7d13628228209553abd5458898b369388'
    }

    configuration = EkstaziConfiguration(configuration_file)
    for test_case in expected_test_hashes:
        test_file, test_name = test_case.split('::', 1)
        test_file = TESTING_PROJECT_ROOT / 'tests' / test_file
        test_hash = configuration.get_test_hash(test_file.name, test_name)
        assert expected_test_hashes[test_case] == test_hash, \
            f'The test hash of "{test_file.name}" are not right'
    
    test_code_readers = TESTING_PROJECT_ROOT / 'tests' / 'test_code_readers.py'
    test_code_readers_content = ''
    with open(test_code_readers) as file:
        test_code_readers_content = file.readlines()
    
    # Edit line 2
    test_code_readers_content[1] = 'from project.database import Database\n'
    # Edit line 5
    test_code_readers_content[4] = '    database = Database()\n'

    edited_test_code_readers_content = ''.join(test_code_readers_content)

    with edit_file_content(test_code_readers, edited_test_code_readers_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        edited_test_case = 'test_code_readers.py::test_read_qr_code'
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(edited_test_case)
        
        for xfail_test_case in XFAIL_TEST_CASES:
            skipped_test_cases.remove(xfail_test_case)
        
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases dependent of modified files did not run again'
        assert results[edited_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'
    
        expected_test_hashes['test_code_readers.py::test_read_qr_code'] = '9d3f2b462862ed8f1932a0b59d446ab60ac28f1b'
        configuration = EkstaziConfiguration(configuration_file)
        test_hash = configuration.get_test_hash('test_code_readers.py', 'test_read_qr_code')
        assert expected_test_hashes[edited_test_case] == test_hash, f'The test hash has not changed correctly'
    

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_results(pytest_options, project_test_cases):
    """
    The plugin should save the result of each test (PASS, FAIL, SKIPPED) in the configuration file 
    at end of the test sesssion.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_results = {
        'test_assert.py::test_assert_false': 'failed',
        'test_assert.py::test_assert_passed': 'passed',
        'test_code_readers.py::test_read_qr_code': 'passed',
        'test_code_readers.py::test_read_barcode': 'failed',
        'test_product.py::test_product_access_level': 'passed',
        'test_product.py::test_delete_product': 'passed',
        'test_product.py::test_insert_product': 'passed',
        'test_product.py::test_unauthorized_access': 'passed'
    }

    configuration = EkstaziConfiguration(configuration_file)
    for test_case in expected_test_results:
        test_file, test_name = test_case.split('::', 1)
        test_file = TESTING_PROJECT_ROOT / 'tests' / test_file
        test_dependencies = configuration.get_last_test_result(test_file.name, test_name)
        assert expected_test_results[test_case] == test_dependencies, \
            f'The test results of "{test_file.name}" are not right'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_test_results_changes(pytest_options, project_test_cases):
    """
    The plugin should save the result of each test (PASS, FAIL, SKIPPED) in the configuration file 
    at end of the test sesssion and when the test file changes the result of the file should change too.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    expected_test_results = {
        'test_assert.py::test_assert_false': 'failed',
        'test_assert.py::test_assert_passed': 'passed',
        'test_code_readers.py::test_read_qr_code': 'passed',
        'test_code_readers.py::test_read_barcode': 'failed',
        'test_product.py::test_product_access_level': 'passed',
        'test_product.py::test_delete_product': 'passed',
        'test_product.py::test_insert_product': 'passed',
        'test_product.py::test_unauthorized_access': 'passed'
    }

    configuration = EkstaziConfiguration(configuration_file)
    for test_case in expected_test_results:
        test_file, test_name = test_case.split('::', 1)
        test_file = TESTING_PROJECT_ROOT / 'tests' / test_file
        test_dependencies = configuration.get_last_test_result(test_file.name, test_name)
        assert expected_test_results[test_case] == test_dependencies, \
            f'The test results of "{test_file.name}" are not right'
    
    new_content = 'def read_qrcode(im_array):\n    return len(im_array) / 3\n\ndef read_barcode(im_array):\n    return len(im_array) / 2\n'
    with edit_file_content(TESTING_PROJECT_ROOT / 'project' / 'readers.py', new_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        failed_tests = ['test_code_readers.py::test_read_qr_code', 'test_code_readers.py::test_read_barcode']
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.FAILED for test in failed_tests), 'Test cases dependent of modified files did not run again'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES if test not in failed_tests), 'Test cases was not marked as xfail'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES and test not in failed_tests), \
        'The other test cases should be marked as skipped'
    
        expected_test_results['test_code_readers.py::test_read_qr_code'] = 'failed'

        configuration = EkstaziConfiguration(configuration_file)
        test_result = configuration.get_last_test_result('test_code_readers.py', 'test_read_qr_code')
        assert expected_test_results['test_code_readers.py::test_read_qr_code'] == test_result, f'The test result has not changed correctly'


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
    with edit_file_content(TESTING_PROJECT_ROOT / 'project' / 'readers.py', new_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        failed_tests = ['test_code_readers.py::test_read_qr_code', 'test_code_readers.py::test_read_barcode']
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.FAILED for test in failed_tests), 'Test cases dependent of modified files did not run again'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES if test not in failed_tests), 'Test cases was not marked as xfail'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES and test not in failed_tests), \
        'The other test cases should be marked as skipped'


@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_changed_test_cases(pytest_options, project_test_cases):
    """The plugin should select test cases that had its steps changed."""
    output = run_pytest(pytest_options)[1]
    assert set(extract_test_case_results(output).keys()) == project_test_cases, 'Some test cases was not selected'
    
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'

    new_content = 'from project.readers import read_qrcode, read_barcode\n\n\ndef test_read_qr_code():\n    assert read_qrcode([1, 2, 3]) == 3\n    assert read_qrcode([1, 2, 3, 4]) == 4\n\n\ndef test_read_barcode():\n    assert read_barcode([0, 1, 0, 1]) == 2\n\n'
    with edit_file_content(TESTING_PROJECT_ROOT / 'tests' / 'test_code_readers.py', new_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        edited_test_case = 'test_code_readers.py::test_read_barcode'
        xfail_test_cases = ['test_assert.py::test_assert_false']
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(edited_test_case)
        skipped_test_cases.remove(xfail_test_cases[0])
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in xfail_test_cases), 'Test cases dependent of modified files did not run again'
        assert results[edited_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_arguments_changed_test_cases(pytest_options, project_test_cases):
    """The plugin should select test cases that had its arguments (fixture) changed."""
    output = run_pytest(pytest_options)[1]
    assert set(extract_test_case_results(output).keys()) == project_test_cases, 'Some test cases was not selected'
    
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'

    test_product = TESTING_PROJECT_ROOT / 'tests' / 'test_product.py'
    test_product_content = ''
    with open(test_product) as file:
        test_product_content = file.readlines()
    
    # Edit line 77
    test_product_content[76] = 'def test_unauthorized_access():\n'
    edited_test_product_content = ''.join(test_product_content)

    with edit_file_content(test_product, edited_test_product_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        edited_test_case = 'test_product.py::test_unauthorized_access'
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(edited_test_case)
        for xfail_test_case in XFAIL_TEST_CASES:
            skipped_test_cases.remove(xfail_test_case)
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases dependent of modified files did not run again'
        assert results[edited_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_select_fixture_steps_changed_test_cases(pytest_options, project_test_cases):
    """The plugin should select test cases that had the steps of its fixtures changed."""
    output = run_pytest(pytest_options)[1]
    assert set(extract_test_case_results(output).keys()) == project_test_cases, 'Some test cases was not selected'

    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'

    conftest = TESTING_PROJECT_ROOT / 'tests' / 'conftest.py'
    conftest_content = ''
    with open(conftest) as file:
        conftest_content = file.readlines()
    
    # Edit line 21
    conftest_content[20] = '    return "I\'m still doing nothing"\n'
    edited_conftest_content = ''.join(conftest_content)

    with edit_file_content(conftest, edited_conftest_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        edited_test_case = 'test_product.py::test_unauthorized_access'
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(edited_test_case)
        for xfail_test_case in XFAIL_TEST_CASES:
            skipped_test_cases.remove(xfail_test_case)
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases dependent of modified files did not run again'
        assert results[edited_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_xfail_cached_failed_test_cases(pytest_options, project_test_cases):
    """
    The plugin shuold mark as xfail test cases would be skipped due no dependency changes or test itself 
    or fixture changes, but it has failed in previous execution.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'

@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_no_ekstazi_selection_option(pytest_options, project_test_cases):
    """
    The plugin should not skip any test case by using Ekstazi selection algorithm when 
    --no-ekstazi-selection flag is provided.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases was not marked as xfail'
    assert all(result == TestResult.SKIPPED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases should be marked as skipped'
    
    output = run_pytest(pytest_options + ['--no-ekstazi-selection'])[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'


@pytest.mark.parametrize('pytest_options', [DEFAULT_PYTEST_OPTIONS, CONFIGURATION_FILE_OPTIONS])
def test_save_new_test_dependency(pytest_options, project_test_cases):
    """
    The plugin should save new test dependencies when the test case had that kind of changing.
    """
    output = run_pytest(pytest_options)[1]
    results = extract_test_case_results(output)
    assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
    assert all(result == TestResult.PASSED for test, result in results.items() if test not in XFAIL_TEST_CASES), \
        'The other test cases (non fail) should be marked as PASSED'
    assert all(results[test] == TestResult.FAILED for test in XFAIL_TEST_CASES), 'Fail test cases was not marked as failed'

    configuration_file = DEFAULT_CONFIG_FILE
    if pytest_options == CONFIGURATION_FILE_OPTIONS:
        configuration_file = CUSTOM_CONFIGURATION_FILE
    
    configuration_file = TESTING_PROJECT_ROOT / 'tests' / configuration_file
    
    test_code_readers = TESTING_PROJECT_ROOT / 'tests' / 'test_code_readers.py'
    configuration = EkstaziConfiguration(configuration_file)
    test_dependencies = configuration.get_test_dependencies(test_code_readers.name, 'test_read_qr_code')
    expected_test_dependencies = [str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py')]

    assert set(test_dependencies) == set(expected_test_dependencies), 'The test dependencies are not right'

    test_code_readers_content = ''
    with open(test_code_readers) as file:
        test_code_readers_content = file.readlines()
    
    # Edit line 2
    test_code_readers_content[1] = 'from project.database import Database\n'
    # Edit line 5
    test_code_readers_content[4] = '    database = Database()\n'

    edited_test_code_readers_content = ''.join(test_code_readers_content)

    with edit_file_content(test_code_readers, edited_test_code_readers_content):
        output = run_pytest(pytest_options)[1]
        results = extract_test_case_results(output)
        edited_test_case = 'test_code_readers.py::test_read_qr_code'
        skipped_test_cases = list(project_test_cases)
        skipped_test_cases.remove(edited_test_case)
        for xfail_test_case in XFAIL_TEST_CASES:
            skipped_test_cases.remove(xfail_test_case)
        assert set(results.keys()) == project_test_cases, 'Some test cases was not selected'
        assert all(results[test] == TestResult.XFAIL for test in XFAIL_TEST_CASES), 'Test cases dependent of modified files did not run again'
        assert results[edited_test_case] == TestResult.PASSED, 'The edit test case should pass after being changed'
        assert all(result == TestResult.SKIPPED for test, result in results.items() if test in skipped_test_cases), \
            'The other test cases should be marked as skipped'
    

    configuration = EkstaziConfiguration(configuration_file)
    new_test_dependencies = configuration.get_test_dependencies(test_code_readers.name, 'test_read_qr_code')
    expected_test_dependencies = [str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'readers.py'), str(TESTING_PROJECT_ROOT / pathlib.Path('project') / 'database.py')]
    
    assert set(new_test_dependencies) == set(expected_test_dependencies), 'The test dependencies was not updated'
