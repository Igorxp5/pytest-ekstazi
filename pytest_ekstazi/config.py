import json
import pathlib
import hashlib


def file_hash(file_path):
    """Calculate SHA1 of the content of a file"""
    with open(file_path, 'rb') as file:
        file_content = file.read()
        return hashlib.sha1(file_content).hexdigest()


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
        self._file_hashes = dict()

        if pathlib.Path(file_path).exists():
            with open(file_path) as file:
                parsed_json = json.load(file)
                depedencies = parsed_json.get('dependencies', self._dependencies)
                file_hashes = parsed_json.get('file_hashes', self._file_hashes)
                if not isinstance(depedencies, dict):
                    raise InvalidConfigurationFile('dependencies is not a dictionary')
                if not isinstance(file_hashes, dict):
                    raise InvalidConfigurationFile('file_hashes is not a dictionary')
                self._dependencies = depedencies
                self._file_hashes = file_hashes
    
    def set_test_dependencies_entry(self, test_file_path, test_name):
        """
        Set an entry of the test in the dependency dictionary. If there's no entry, an empty list
        is set, otherwise do nothing.

        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._dependencies.setdefault(test_key, [])
    
    def add_test_dependency(self, test_file_path, test_name, depedency_file_path):
        """
        Add a new dependency file to test case

        :param test_file_path Script location of the test case
        :param test_name Test function name
        :param depedency_file_path Dependency file path
        """
        test_key = self.get_test_key(test_file_path, test_name)
        self._dependencies.setdefault(test_key, [])
        self._dependencies[test_key].append(str(depedency_file_path))
    
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
    
    def add_file_hash(self, file_path):
        """Add or update the hash value of a file. This function calculates SHA-1 hash of the file content.
        
        :param file_path Location of the file
        :param file_hash Hash value of the file content
        """
        file_path = str(file_path)
        self._file_hashes[file_path] = file_hash(file_path)

    def get_file_hash(self, file_path):
        return self._file_hashes[file_path]

    def save(self):
        """Save the dependencies and file hashes into the configuration file"""
        json_content = {'dependencies': self._dependencies, 'file_hashes': self._file_hashes}
        with open(self._file_path, 'w') as file:
            json.dump(json_content, file, indent=4)
    
    @staticmethod
    def get_test_key(test_file_path, test_name):
        """
        Get the key in the dependency dictionary of the test case
        
        :param test_file_path Script location of the test case
        :param test_name Test function name
        """
        return '{}::{}'.format(test_file_path, test_name)
    
    def extract_test_from_key(test_key):
        """
        Extract test file name and test name from a dependency dictionary key
        
        :param test_key Dependency dictionary key
        """
        return test_key.split('::', 1)
