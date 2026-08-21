# Contributing Guide

Thank you for your interest in contributing to py-img-processor! This guide walks you through the development workflow.

## Prerequisites

- Python >= 3.9
- [pre-commit](https://pre-commit.com/)
- (Optional) [tox](https://tox.wiki/) for multi-version testing

## Setting Up the Development Environment

1. **Clone the repository and create a virtual environment:**

```bash
git clone https://github.com/skylerhu/py-img-processor.git
cd py-img-processor
python3.9 -m venv .env
source .env/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements_dev.txt
pip install -e ./          # editable install for development
```

3. **Set up pre-commit hooks:**

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## Project Structure

| Path | Description |
| --- | --- |
| `imgprocessor/` | Core library source code |
| `tests/` | Test suite |
| `tests/conftest.py` | Pytest global fixtures |
| `tests/settings/` | Django-compatible settings for tests |
| `docs/` | Documentation (MkDocs) |
| `Makefile` | Build, test, and release commands (run `make help`) |
| `pytest.ini` | Pytest configuration |
| `.coveragerc` | Coverage configuration (referenced by pytest.ini) |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `tox.ini` | Multi-Python-version test matrix |
| `MANIFEST.in` | Packaging manifest |

## Running Tests

```bash
# Run the full test suite
pytest tests

# Run tests across all Python versions
tox run
```

To save processed images under `.tmp/output/` for visual comparison with `tests/imgs/expected`:

```bash
pytest tests --use_special_tmp
```

## Commit Message Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>
```

Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `perf`, `test`, `build`.

## Submitting a Pull Request

Before submitting a PR, please verify:

- [ ] New code includes test cases
- [ ] All tests pass — `make test-all`
- [ ] Coverage requirements met — `make coverage`
- [ ] Local package builds successfully — `make dist`

## Building Documentation

```bash
mkdocs build --clean    # generate the static site
mkdocs serve            # start a local preview server
```

Documentation is published via [Read the Docs](https://readthedocs.org/). Builds are triggered manually from the ReadTheDocs dashboard.

## Packaging & Release

All commands below are defined in the `Makefile`:

```bash
make clean-build                                    # remove build cache
python setup.py sdist bdist_wheel                   # build source and wheel
twine check dist/py*(.whl|.tar.gz)                  # verify package metadata
twine upload -r pypi dist/py*(.whl|.tar.gz)         # upload to PyPI
```

> PyPI upload requires credentials configured in `~/.pypirc`.

## Notes

- Consider [pillow-simd](https://github.com/uploadcare/pillow-simd) for improved performance — see [benchmarks](https://python-pillow.org/pillow-perf/).
