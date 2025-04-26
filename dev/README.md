## Development Tools

This folder contains helper scripts and tools to assist in the development of the project.

* `run_tests.sh`: run all tests in the project. The tests can be found in the `tests/` folder.
* `run_coverage.sh`: measure code coverage during execution of the tests, and opens a report in the browser.
* `run_pylint.sh`: run the linter on the project code using the [PEP 8](https://peps.python.org/pep-0008/) guidelines.

(Use `chmod +x ...` if needed to allow these scripts to run.)

### Disclaimer

Please note that these script were used during development on a Linux system with certain software installed (e.g. Firefox). They are **not intended to be used by the end-user**, and may need to be modified to work on other systems.

### Virtual Environment

These scripts were run from within a virtual environment, which is recommended to avoid conflicts with other Python packages. To create a virtual environment, run:

```bash
python3 -m venv venv
```

Then, activate the virtual environment:

```bash
source venv/bin/activate
```

To install the required packages ([coverage](https://coverage.readthedocs.io/en/7.4.4) and [pylint](https://pypi.org/project/pylint/)) inside the environment, run:

```bash
pip install coverage pylint
```

You can then safely run the scripts from the activated virtual environment. For example, to run the tests, use:

```bash
./dev/run_tests.sh
```

To deactivate the virtual environment, run:

```bash
deactivate
```