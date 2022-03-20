# pytest-ekstazi

pytest-ekstazi is a plugin for pytest that selects the test cases that need to be run based on the Ekstazi algorithm.

![license](https://img.shields.io/github/license/Igorxp5/pytest-ekstazi) ![pyversion](https://img.shields.io/pypi/pyversions/pytest) ![pypi](https://img.shields.io/pypi/v/pytest-ekstazi)

## Requirements

You will need the following prerequisites in order to use pytest-ekstazi:
- Python 3.7 or newer
- Pytest 6.0.0 or newer

## Installation

To install pytest-ekstazi:

```shell
pip install pytest-ekstazi
```

## Selecting the test cases

Use the `--ekstazi` command line option to enable the plugin. For the first session the plugin is going to run the entire test suite and map the depedencies of each test function. The next executions, Ekstazi is going to check for each test function if their dependency files have changed. Just test cases with depedencies that have changed will run.

```shell
pytest --ekstazi .
```

For every run, the plugin saves/updates the dependency tree, last test results and dependency hashes in a configuration file. By default the configuration file is saved in working directory under name `ekstazi.json`. You can change the configuration file location by doing:

```shell
pytest --ekstazi --ekstazi-file path/to/bar.json
```

**Run the plugin always in the same directory or pass full path of the configuration file, otherwise the plugin will not be able to select the test case based on previous result.**

## Development

To setup the development environment, first make sure `Python >= 3.7` is installed in your machine. So clone the repo:

```shell
git clone https://github.com/Igorxp5/pytest-ekstazi.git
```

Open the project directory and install the plugin in **editable-mode**:

```shell
pip install -e .
```

## Credits

Ekstazi is Regression Test Selection algorithm created by Milos Gligoric, Lamyaa Eloussi, and Darko Marinov. Check out the their [research paper](http://ekstazi.org/research.html).
