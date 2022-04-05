import re
import sys
import trace
import pathlib
import functools

import pytest

from .config import EkstaziConfiguration, file_hash

DEFAULT_CONFIG_FILE = pathlib.Path.cwd() / 'ekstazi.json'
IGNORABLE_FILE = re.compile(r'\<.+\>')


class EkstaziPytestPlugin:
    # ignorable modules dirs (Python internal modules) 
    _ignore_dirs = [sys.prefix, sys.exec_prefix]

    def __init__(self, configuration):
        self._tracers = dict()
        self._configuration = configuration

    def pytest_pyfunc_call(self, pyfuncitem):
        test_name = pyfuncitem.originalname
        test_function = pyfuncitem.obj
        test_location = pyfuncitem.fspath
        test_location = self._get_relative_file_path(test_location)

        test_key = EkstaziConfiguration.get_test_key(test_location, test_name)
        tracer = trace.Trace(trace=0, count=1, countfuncs=1, ignoredirs=EkstaziPytestPlugin._ignore_dirs)
        self._tracers[test_key] = tracer

        @functools.wraps(test_function)
        def tracer_wrapper(*args, **kwargs):
            tracer.runfunc(test_function, *args, **kwargs)

        pyfuncitem.obj = tracer_wrapper
    
    def pytest_sessionfinish(self, session, exitstatus):
        dependency_files = set()
        for test_key, tracer in self._tracers.items():
            test_location, test_name = EkstaziConfiguration.extract_test_from_key(test_key)
            results = tracer.results()
            self._configuration.remove_dependencies(test_location, test_name)
            self._configuration.set_test_dependencies_entry(test_location, test_name)
            calls = sorted(results.calledfuncs)
            for filename, _, funcname in calls:
                # ignore Python internal calls and the test itself
                if all(not filename.startswith(path) for path in self._ignore_dirs) \
                        and filename != test_location and funcname != test_name \
                        and not IGNORABLE_FILE.match(filename):
                    filename = self._get_relative_file_path(filename)
                    self._configuration.add_test_dependency(test_location, test_name, filename)
                    if filename not in dependency_files:
                        self._configuration.add_file_hash(filename)
                        # add file to a set, so we can avoid recalculate the hash for the same dependency
                        dependency_files.add(filename)
        self._configuration.save()

    def pytest_collection_modifyitems(self, config, items):
        skip = pytest.mark.skip(reason='The test dependencies was not changed since the last test execution')
        dependencies_hashes = dict()
        for item in items:
            test_name = item.originalname
            test_location = item.fspath
            test_location = self._get_relative_file_path(test_location)
            dependencies = self._configuration.get_test_dependencies(test_location, test_name)
            if dependencies:
                for dependency in dependencies:
                    dependencies_hashes.setdefault(dependency, file_hash(dependency))

            # If all dependencies are the same, the test case is skipped
            if all(dependencies_hashes[d] == self._configuration.get_file_hash(d) for d in dependencies):
                item.add_marker(skip)

    @staticmethod
    def _get_relative_file_path(file_path):
        return pathlib.Path(file_path).relative_to(pathlib.Path.cwd())


def pytest_configure(config):
    if config.getvalue('use_ekstazi'):
        configuration = EkstaziConfiguration(config.getvalue('ekstazi_file'))
        config.pluginmanager.register(EkstaziPytestPlugin(configuration), 'ekstazi_plugin')


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
