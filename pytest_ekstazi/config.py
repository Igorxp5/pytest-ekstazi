import enum
import json
import pathlib


class TestOutcome(str, enum.Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    ERROR = 'error'


class InvalidConfigurationFile(ValueError):
    pass


class EkstaziConfiguration:
    def __init__(self, file_path):
        """
        Parse a Ekstazi Configuration file
        
        :param file_path Configuration file path.
        """
        self._file_path = file_path
        self._dependencies = dict()
        self._dependencies_hashes = dict()
        self._test_hashes = dict()
        self._test_results = dict()

        if pathlib.Path(file_path).exists():
            with open(file_path) as file:
                parsed_json = json.load(file)
                json_objects = {'dependencies': self._dependencies, 'dependencies_hashes': self._dependencies_hashes,
                                'test_hashes': self._test_hashes, 'test_results': self._test_results}
                for key, local_dict in json_objects.items():
                    json_object = parsed_json.get(key, local_dict) 
                    if not isinstance(json_object, dict):
                        raise InvalidConfigurationFile('{} is not a dictionary'.format(key))
                    local_dict.update(json_object)

                # convert test result values to TestOutcome object
                self._test_results = {key: TestOutcome(value) for key, value in self._test_results.items()}

    def set_test_dependencies_entry(self, test_file_path, test_name):
        """
        Set an entry of the test in the dependency dictionary. If there's no entry, an empty list
        is set, otherwise do nothing.

        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._dependencies.setdefault(test_key, set())
    
    def add_test_dependency(self, test_file_path, test_name, depedency_file_path):
        """
        Add a new dependency file to test case

        :param test_file_path Script location of the test case
        :param test_name Test function name
        :param depedency_file_path Dependency file path
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._dependencies.setdefault(test_key, set())
        self._dependencies[test_key].add(str(depedency_file_path))
    
    def get_test_dependencies(self, test_file_path, test_name):
        """
        Get dependencies of a test. The method returns None if dependencies have not been discovered.

        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        return self._dependencies.get(test_key)

    def remove_dependencies(self, test_file_path, test_name):
        """
        Remove a dependecy file
        
        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        if test_key in self._dependencies: 
            del self._dependencies[test_key]
    
    def add_dependency_hash(self, file_path, hashdigest):
        """Add or update the hash value of a file. This function calculates SHA-1 hash of the file content.
        
        :param file_path Location of the file
        :param hashdigest Hash hexdigest of the file
        """
        file_path = str(file_path)
        self._dependencies_hashes[file_path] = hashdigest
    
    def add_test_hash(self, test_file_path, test_name, hashdigest):
        """Add or update the hash value of a test file. This function calculates SHA-1 hash of the file content.
        
        :param test_file_path Location of the test
        :param test_name Test function name
        :param hashdigest Hash hexdigest of the test
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._test_hashes[test_key] = hashdigest
    
    def set_test_result(self, test_file_path, test_name, outcome):
        """
        Set the result of the test
        
        :param test_file_path Script location of the test case
        :param test_name Test function name
        :param outcome TestOutcome object defining the result of the test
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._test_results[test_key] = outcome

    def get_dependency_hash(self, file_path):
        """Get the hash of the content of a depedency file saved in the configuration 

        :param file_path Location of the file
        """
        return self._dependencies_hashes.get(str(file_path))
    
    def get_test_hash(self, test_file_path, test_name):
        """Get the hash of the content of a test file saved in the configuration 

        :param test_file_path Location of the test
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        return self._test_hashes.get(test_key)
    
    def get_last_test_result(self, test_file_path, test_name):
        """
        Get result of the test saved in the configuration
        
        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        return self._test_results.get(test_key)

    def save(self):
        """Save the dependencies and file hashes into the configuration file"""
        json_content = {'dependencies': {d: list(self._dependencies[d]) for d in self._dependencies},
                        'dependencies_hashes': self._dependencies_hashes,
                        'test_hashes': self._test_hashes,
                        'test_results': self._test_results}
        with open(self._file_path, 'w') as file:
            json.dump(json_content, file, indent=4)
    
    @staticmethod
    def get_test_key(test_file_path, test_name):
        """
        Get the key in the dependency dictionary of the test case
        
        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        return '{}::{}'.format(pathlib.Path(test_file_path).name, test_name)
    
    def extract_test_from_key(test_key):
        """
        Extract test file name and test name from a dependency dictionary key
        
        :param test_key Dependency dictionary key
        """
        return test_key.split('::', 1)
