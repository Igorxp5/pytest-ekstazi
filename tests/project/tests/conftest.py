import os
import pathlib

import pytest

from project.database import DEFAULT_DATABASE_FILE


@pytest.fixture(autouse=True)
def delete_database_file():
    database_filepath = pathlib.Path(DEFAULT_DATABASE_FILE)
    if database_filepath.exists():
        os.remove(database_filepath)
    yield
    if database_filepath.exists():
        os.remove(database_filepath)
