__author__ = ['Igorxp5', 'vsla', 'Nielx20']

__license__ = 'MIT'
__version__ = '0.0.0'

import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setuptools.setup(
    name='py-ekstazi',
    version=__version__,
    author=__author__,
    description='Pytest plugin to select test using Ekstazi algorithm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Igorxp5/py-ekstazi',
    packages=['py_ekstazi'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Pytest'
    ],
    entry_points={
        'pytest11': ['py_ekstazi = py_ekstazi.plugin']
    },
    install_requires=['pytest'],
    python_requires='>=3.6',
)
