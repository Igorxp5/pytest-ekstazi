__author__ = 'Igorxp5, vsla, Nielx20'

__license__ = 'MIT'
__version__ = '1.0.0'

import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setuptools.setup(
    name='pytest-ekstazi',
    version=__version__,
    author=__author__,
    description='Pytest plugin to select test using Ekstazi algorithm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Igorxp5/pytest-ekstazi',
    packages=['pytest_ekstazi'],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Pytest'
    ],
    entry_points={
        'pytest11': ['pytest_ekstazi = pytest_ekstazi.plugin'],
        'console_scripts': ['ekstazi_matrix = pytest_ekstazi.console_scripts:ekstazi_matrix']
    },
    install_requires=['pytest', 'Jinja2'],
    python_requires='>=3.7',
)
