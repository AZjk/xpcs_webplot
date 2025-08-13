# Development Setup

This project uses a modern Python package structure with `src` layout and `pyproject.toml` configuration.

## Project Structure

```
xpcs_webplot/
├── src/
│   └── xpcs_webplot/       # Main package code
│       ├── templates/      # HTML templates
│       └── ...            # Python modules
├── tests/                  # Test files
├── pyproject.toml         # Project configuration and dependencies
├── requirements.txt       # Direct dependencies (for pip install)
└── README.rst            # Project documentation
```

## Installation

### For Development

Install the package in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

This will install:
- The package in editable mode (changes to source code are immediately reflected)
- All runtime dependencies (numpy, h5py, matplotlib, jinja2, flask)
- Development tools (pytest, black, flake8, mypy, pre-commit)

### For Users

```bash
pip install .
```

Or directly from requirements.txt:

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=xpcs_webplot --cov-report=term-missing
```

## Code Formatting

Format code with Black:

```bash
black src tests
```

Check code style:

```bash
flake8 src tests
```

Sort imports:

```bash
isort src tests
```

## Type Checking

```bash
mypy src
```

## Available Commands

After installation, these commands are available:

- `xpcs_webplot` - Main CLI tool
- `xpcs_webplot_server` - Flask development server
- `xpcs_webplot_migrate` - Migration tool for Flask conversion
