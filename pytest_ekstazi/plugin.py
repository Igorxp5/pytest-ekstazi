import re
import sys
import trace
import pathlib
import inspect
import hashlib
import functools

import pytest

from .config import EkstaziConfiguration, TestOutcome
from .utils import file_hash

DEFAULT_CONFIG_FILE = pathlib.Path.cwd() / 'ekstazi.json'
TRACE_IGNORE_FILES = re.compile(r'\<.+\>')


class EkstaziPytestPlugin:
    # ignorable modules dirs (Python internal modules) 
    _ignore_dirs = [sys.prefix, sys.exec_prefix]

    def __init__(self, configuration, rootdir, select_tests=True):
        """
        Create instance of Ekstazi Pytest plugin

        :param configuration EkstaziConfiguration object
        :param rootdir Pytest root dir
        :param select_tests Enable test selection phase
        """
        self._tracers = dict()
        self._pyfuncitems = dict()
        self._test_results = dict()
        self._configuration = configuration
        self._rootdir = rootdir
        self._select_tests = select_tests

        # caching the hashes of the files to avoid re-calculate every pytest_runtest_setup call 
        self._dependencies_hashes = dict()
        self._test_hashes = dict()
        self._fixture_hashes = dict()

    def pytest_runtest_setup(self, item):
        if not self._select_tests:
            return None

        test_name = item.originalname
        test_location = item.fspath
        test_location = self._get_relative_file_path(test_location)
        dependencies = self._configuration.get_test_dependencies(test_location, test_name)
        if dependencies:
            for dependency in dependencies:
                self._dependencies_hashes.setdefault(dependency, file_hash(dependency))

        # if the test dependencies has been already identified and all dependencies are the same (or the test does not have any dependency) 
        # and its test file is the same the should be skipped.
        # when the last test execution has resulted in fail, an xfail is thrown
        if dependencies is not None and all(self._dependencies_hashes[d] == self._configuration.get_dependency_hash(d) for d in dependencies):
            test_key = EkstaziConfiguration.get_test_key(test_location, test_name)
            self._test_hashes[test_key] = self._get_pyfuncitem_hash(item._pyfuncitem)
            if self._test_hashes[test_key] == self._configuration.get_test_hash(test_location, test_name):
                test_result = self._configuration.get_last_test_result(test_location, test_name)
                if test_result in (TestOutcome.ERROR, TestOutcome.FAILED):
                    raise pytest.xfail.Exception('The test has failed in the last execution and its dependencies have not changed')
                elif test_result == TestOutcome.PASSED:
                    raise pytest.skip.Exception('The test and its dependencies were not changed since the last test execution')

    def pytest_pyfunc_call(self, pyfuncitem):
        test_name = pyfuncitem.originalname
        test_function = pyfuncitem.obj
        test_location = pyfuncitem.fspath
        test_location = self._get_relative_file_path(test_location)

        test_key = EkstaziConfiguration.get_test_key(test_location, test_name)
        tracer = trace.Trace(trace=0, count=1, countfuncs=1, ignoredirs=EkstaziPytestPlugin._ignore_dirs)
        self._tracers[test_key] = tracer
        self._pyfuncitems[test_key] = pyfuncitem

        @functools.wraps(test_function)
        def tracer_wrapper(*args, **kwargs):
            tracer.runfunc(test_function, *args, **kwargs)

        pyfuncitem.obj = tracer_wrapper
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        result = outcome.get_result()

        if result.when == 'setup' and result.outcome == 'failed':
            self._test_results[item] = TestOutcome.ERROR
        elif result.when == 'call' and result.outcome == 'failed':
            self._test_results[item] = TestOutcome.FAILED
        elif result.when == 'call' and result.outcome == 'passed':
            self._test_results[item] = TestOutcome.PASSED
        elif result.when == 'call' and result.outcome == 'skipped':
            self._test_results[item] = TestOutcome.SKIPPED

    def pytest_sessionfinish(self, session, exitstatus):
        # save test and test dependencies hashes
        dependency_files = set()
        for test_key, tracer in self._tracers.items():
            test_location, test_name = EkstaziConfiguration.extract_test_from_key(test_key)
            results = tracer.results()
            self._configuration.remove_dependencies(test_location, test_name)
            if test_key not in self._test_hashes:
                self._test_hashes[test_key] = self._get_pyfuncitem_hash(self._pyfuncitems[test_key])
            self._configuration.add_test_hash(test_location, test_name, self._test_hashes[test_key])
            self._configuration.set_test_dependencies_entry(test_location, test_name)
            calls = sorted(results.calledfuncs)
            for filename, _, funcname in calls:
                # ignore Python internal calls and the test itself
                if all(not filename.startswith(path) for path in self._ignore_dirs) \
                        and filename != test_location and funcname != test_name \
                        and not TRACE_IGNORE_FILES.match(filename):
                    filename = self._get_relative_file_path(filename)
                    self._configuration.add_test_dependency(test_location, test_name, filename)
                    if filename not in dependency_files:
                        self._configuration.add_dependency_hash(filename, file_hash(filename))
                        # add file to a set, so we can avoid recalculate the hash for the same dependency
                        dependency_files.add(filename)
        # save test results
        for item, outcome in self._test_results.items():
            self._configuration.set_test_result(item.fspath, item.originalname, outcome)
        self._configuration.save()

    def _get_relative_file_path(self, file_path):
        return pathlib.Path(file_path).relative_to(self._rootdir)
    
    def _get_pyfuncitem_hash(self, pyfuncitem):
        hashes = []
        for fixture_name in pyfuncitem.fixturenames:
            fixture_def = pyfuncitem._fixtureinfo.name2fixturedefs[fixture_name][0]
            cache_key = '{}_{}'.format(fixture_def.baseid, fixture_def.argname)
            if cache_key not in self._fixture_hashes:
                fixture_content = inspect.getsource(fixture_def.func).encode()
                fixture_hash = hashlib.sha1(fixture_content).hexdigest()
                self._fixture_hashes[cache_key] = fixture_hash
            hashes.append(self._fixture_hashes[cache_key])
        function_content = inspect.getsource(pyfuncitem.obj).encode()
        hashes.append(hashlib.sha1(function_content).hexdigest())
        return hashlib.sha1('\n'.join(hashes).encode()).hexdigest()


def pytest_configure(config):
    if config.getvalue('use_ekstazi'):
        configuration = EkstaziConfiguration(config.getvalue('ekstazi_file'))
        select_tests = config.getvalue('ekstazi_selection')
        config.pluginmanager.register(EkstaziPytestPlugin(configuration, config.rootdir, select_tests), 'ekstazi_plugin')


def pytest_addoption(parser):
    """Add plugin CLI options"""

    parser.addoption(
        '--ekstazi',
        dest='use_ekstazi',
        action='store_true',
        default=False,
        help='Enable Ekstazi plugin.'
    )

    parser.addoption(
        '--ekstazi-file',
        dest='ekstazi_file',
        default=DEFAULT_CONFIG_FILE,
        help='Ekstazi configuration file. '
             'The file contains the test cases\' file dependencies and the hashes of their content.'
    )

    parser.addoption(
        '--no-ekstazi-selection',
        dest='ekstazi_selection',
        action='store_false',
        default=True,
        help='Selection phase of Ekstazi plugin is skipped. The hashes and test dependencies '
             'is still calculated and updated at end of the test session.'
    )
