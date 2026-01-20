# Development Guide

Guide for developers who want to contribute to XPCS WebPlot.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of:
  - XPCS data analysis
  - HDF5 file format
  - Python packaging
  - Web development (for Flask components)

### Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/xpcs_webplot.git
cd xpcs_webplot
```

## Development Setup

### Install in Development Mode

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with development dependencies
pip install -e ".[dev]"
```

This installs:
- The package in editable mode (changes reflected immediately)
- All runtime dependencies
- Development tools (pytest, black, flake8, mypy, pre-commit)

### Verify Installation

```bash
# Check that commands are available
xpcs_webplot --help
xpcs_webplot_server --help

# Run tests to verify setup
pytest
```

### Project Structure

```
xpcs_webplot/
├── src/
│   └── xpcs_webplot/          # Main package
│       ├── __init__.py
│       ├── cli.py             # CLI entry point
│       ├── converter.py       # Core conversion logic
│       ├── webplot_cli.py     # Workflow management
│       ├── flask_app.py       # Web server
│       ├── plot_images.py     # Plotting functions
│       ├── html_utlits.py     # HTML generation
│       ├── monitor_and_process.py  # Monitoring
│       ├── metadata_utils.py  # Metadata handling
│       └── templates/         # Jinja2 templates
│           ├── flask_index.html
│           ├── flask_result.html
│           └── mini-preview/
├── tests/                     # Test files
│   ├── test_xpcs_webplot.py
│   └── test_flask_server.py
├── docs/                      # Documentation
├── pyproject.toml            # Project configuration
├── README.rst                # Project README
├── LICENSE                   # MIT License
└── Makefile                  # Development commands
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Docstrings**: NumPy style
- **Imports**: Sorted with isort (Black-compatible profile)
- **Type hints**: Encouraged but not required

### Formatting with Black

```bash
# Format all code
black src tests

# Check without modifying
black --check src tests
```

### Linting with Flake8

```bash
# Check code style
flake8 src tests

# Common issues to avoid:
# - Unused imports
# - Undefined names
# - Line too long (>88 chars)
```

### Import Sorting with isort

```bash
# Sort imports
isort src tests

# Check without modifying
isort --check src tests
```

### Type Checking with mypy

```bash
# Run type checker
mypy src

# Note: Type hints are encouraged but not strictly enforced
```

### Pre-commit Hooks

Set up pre-commit hooks to automatically check code before committing:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Docstring Style

Use NumPy-style docstrings for all public functions and classes:

```python
def example_function(param1, param2, optional_param=None):
    """
    Brief description of function.

    Longer description with more details about what the function does,
    how it works, and any important considerations.

    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
    optional_param : bool, optional
        Description of optional parameter (default: None)

    Returns
    -------
    result_type
        Description of return value

    Raises
    ------
    ValueError
        When param1 is invalid
    FileNotFoundError
        When file doesn't exist

    See Also
    --------
    related_function : Related functionality

    Examples
    --------
    >>> example_function('test', 42)
    'result'

    Notes
    -----
    Additional notes about implementation details or usage.
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xpcs_webplot --cov-report=term-missing

# Run specific test file
pytest tests/test_xpcs_webplot.py

# Run specific test function
pytest tests/test_xpcs_webplot.py::test_specific_function

# Run with verbose output
pytest -v
```

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_converter.py
import pytest
from pathlib import Path
from xpcs_webplot.converter import convert_xpcs_result

def test_convert_xpcs_result_basic():
    """Test basic conversion functionality."""
    # Arrange
    input_file = Path('test_data/sample.hdf')
    output_dir = Path('test_output')
    
    # Act
    result = convert_xpcs_result(input_file, target_dir=output_dir)
    
    # Assert
    assert result is True
    assert (output_dir / 'sample' / 'summary.html').exists()

def test_convert_xpcs_result_invalid_file():
    """Test handling of invalid input file."""
    with pytest.raises(FileNotFoundError):
        convert_xpcs_result('nonexistent.hdf')
```

### Test Coverage

Aim for:
- **Overall coverage**: >80%
- **Critical paths**: 100%
- **Error handling**: Well-tested

Check coverage:

```bash
# Generate coverage report
pytest --cov=xpcs_webplot --cov-report=html

# View in browser
open htmlcov/index.html
```

### Test Data

- Store test data in `test_data/` directory
- Use small, representative HDF5 files
- Document test data sources and formats
- Don't commit large files (use Git LFS if needed)

## Contributing

### Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** following code style guidelines

3. **Add tests** for new functionality

4. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   black src tests
   flake8 src tests
   ```

5. **Commit changes** with clear messages:
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request** on GitHub

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed, explaining what changed and why.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(converter): add support for new HDF5 format

fix(flask_app): correct subdirectory navigation bug

docs(api): update API reference for converter module

test(converter): add tests for error handling
```

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what changed and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs if needed
- **Code style**: Ensure all checks pass
- **Small PRs**: Keep changes focused and manageable

### Code Review

All contributions require code review:

- Address reviewer feedback promptly
- Be open to suggestions
- Explain your design decisions
- Update PR based on feedback

## Development Tasks

### Common Tasks

Use the Makefile for common development tasks:

```bash
# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Clean build artifacts
make clean

# Build package
make build

# Install in development mode
make install-dev
```

### Adding New Features

1. **Plan the feature**:
   - Write design document if complex
   - Discuss in GitHub issue
   - Get feedback from maintainers

2. **Implement**:
   - Write code following style guide
   - Add comprehensive docstrings
   - Include type hints where appropriate

3. **Test**:
   - Write unit tests
   - Write integration tests if needed
   - Ensure good coverage

4. **Document**:
   - Update API reference
   - Update user guide if user-facing
   - Add examples

5. **Submit PR**:
   - Follow PR guidelines
   - Link to related issues
   - Request review

### Fixing Bugs

1. **Reproduce the bug**:
   - Create minimal test case
   - Document steps to reproduce

2. **Write failing test**:
   - Test should fail with current code
   - Test should pass after fix

3. **Fix the bug**:
   - Make minimal changes
   - Don't introduce new features

4. **Verify fix**:
   - Ensure test passes
   - Check for regressions
   - Test edge cases

5. **Submit PR**:
   - Reference issue number
   - Explain root cause
   - Describe solution

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backwards-compatible
- **PATCH**: Bug fixes, backwards-compatible

Examples:
- `0.0.1` → `0.0.2`: Bug fix
- `0.0.2` → `0.1.0`: New feature
- `0.1.0` → `1.0.0`: Breaking change

### Release Checklist

1. **Update version** in `pyproject.toml`

2. **Update CHANGELOG**:
   - List all changes since last release
   - Categorize: Added, Changed, Fixed, Removed

3. **Run full test suite**:
   ```bash
   pytest
   black --check src tests
   flake8 src tests
   mypy src
   ```

4. **Build package**:
   ```bash
   python -m build
   ```

5. **Test installation**:
   ```bash
   pip install dist/xpcs_webplot-*.whl
   xpcs_webplot --help
   ```

6. **Create git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

7. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

8. **Create GitHub release**:
   - Go to GitHub releases
   - Create new release from tag
   - Add release notes

## Debugging

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Debugging

Use Python debugger:

```python
import pdb; pdb.set_trace()
```

Or use IPython debugger:

```python
from IPython import embed; embed()
```

### Common Issues

**Import errors after changes**:
```bash
# Reinstall in editable mode
pip install -e .
```

**Tests failing unexpectedly**:
```bash
# Clear pytest cache
pytest --cache-clear
```

**Flask app not updating**:
```bash
# Restart with debug mode
xpcs_webplot serve --debug
```

## Resources

### Documentation

- [Python Packaging Guide](https://packaging.python.org/)
- [NumPy Docstring Guide](https://numpydoc.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)

### Tools

- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [mypy](https://mypy.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or share ideas
- **Email**: Contact maintainers directly

## See Also

- [User Guide](user_guide.md) - Using the package
- [API Reference](api_reference.md) - API documentation
- [Architecture](architecture.md) - System design
