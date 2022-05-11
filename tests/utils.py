import re
import enum
import logging
import subprocess
import contextlib

from .constants import TESTING_PROJECT_TEST_ROOT

LOGGER = logging.getLogger(__name__)


class TestResult(enum.Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    XFAIL = 'xfail'
    XFAILED = 'xfailed'
    ERRORS = 'errors'
    ERROR = 'error'


def run_pytest(optional_args=None, timeout=30):
    """
    Run Pytest proccess by providing optional arguments to it
    
    :param optional_args Optional arguements to Pytest process
    :param timeout Time limit to pytest process exit
    :return process exit code, standard output and stdard error 
    """
    optional_args = optional_args or []
    process = subprocess.Popen(['pytest'] + optional_args + ['-sv', '.'],
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                               text=True, cwd=TESTING_PROJECT_TEST_ROOT)
    process.wait(timeout=timeout)
    
    stdout = process.stdout.read()
    stderr = process.stderr.read()
    
    LOGGER.debug(f'==== PYTEST STDOUT ====')
    LOGGER.debug(stdout)
    LOGGER.debug(f'==== PYTEST STDERR ====')
    LOGGER.debug(stderr)
    
    return process.returncode, stdout, stderr


def extract_pytest_results(pytest_output):
    """
    Get total of passed, failed, xfailed and skipped in a pytest report

    :param pytest_output stdout of pytest execution
    :rtype Dict[TestResult, int]
    """
    report_pattern = re.compile(r'=+ (.+) in [0-9\.]+s =+')
    raw_results = report_pattern.search(pytest_output.split('\n')[-2]).group(1).split(',')
    result_pattern = re.compile(r'(\d+) ([a-z]+)')

    results = dict()
    for raw_test_result in raw_results:
        match = result_pattern.search(raw_test_result)
        test_result = TestResult(match.group(2))
        total = int(match.group(1))
        results[test_result] = total
    return results

def extract_test_case_results(pytest_output):
    """
    Get result of each test case ran in a pytest execution

    :param pytest_output stdout of pytest execution
    :rtype Dict[str, TestResult]
    """
    lines = pytest_output.split('\n')
    start_index = 0
    while not re.match(r'(collecting ... )?collected \d+ items', lines[start_index]):
        start_index += 1

    results = dict()
    index = start_index + 2
    while lines[index].strip():
        line = lines[index]
        raw_split = line.split(' ', 2)
        test_result = TestResult(raw_split[1].lower())
        test_case = raw_split[0]
        results[test_case] = test_result
        index += 1
    return results


@contextlib.contextmanager
def edit_file_content(filepath, new_content):
    """Re-write a file and recover the original content when out of the context"""
    original_content = ''
    with open(filepath) as file:
        original_content = file.read()
    with open(filepath, 'w') as file:
        file.write(new_content)
    try:
        yield
    finally:
        with open(filepath, 'w') as file:
            file.write(original_content)
