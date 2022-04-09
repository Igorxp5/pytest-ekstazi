import hashlib


def file_hash(file_path):
    """Calculate SHA1 of the content of a file"""
    with open(file_path, 'rb') as file:
        file_content = file.read()
        return hashlib.sha1(file_content).hexdigest()
