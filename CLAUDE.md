# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XPCS WebPlot is a Python package for converting X-ray Photon Correlation Spectroscopy (XPCS) analysis results (HDF5 files) into interactive web-viewable formats. It provides batch processing, real-time monitoring, and a Flask-based web server for browsing results.

## Development Commands

### Installation

```bash
# Development installation (recommended)
pip install -e ".[dev]"

# User installation
pip install .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xpcs_webplot --cov-report=term-missing

# Run specific test
pytest tests/test_xpcs_webplot.py -k test_function_name
```

### Code Quality

```bash
# Format code
black src tests

# Check style
flake8 src tests

# Sort imports
isort src tests

# Type checking
mypy src
```

### Package Commands

```bash
# Main CLI tool
xpcs_webplot

# Flask development server (alternative to 'serve' subcommand)
xpcs_webplot_server

# Prepare HTML for serving
xpcs_webplot_prepare
```

## Architecture

### Source Layout

This project uses the modern `src` layout:
- `src/xpcs_webplot/` - Main package code (NOT `xpcs_webplot/` at root)
- `tests/` - Test files
- `pyproject.toml` - Project configuration and dependencies

**Important**: Always import from the installed package, never add the root directory to PYTHONPATH. This ensures tests run against the installed version.

### Multi-Layer Architecture

```
User Interfaces (CLI, Web, API)
         ↓
Core Processing Layer (converter.py, webplot_cli.py, monitor_and_process.py)
         ↓
Visualization Layer (plot_images.py, html_utlits.py, metadata_utils.py)
         ↓
Data Layer (pyxpcsviewer for HDF5, file system output)
```

### Key Modules

**Entry Points:**
- `cli.py` - Main CLI with subcommands (plot, combine, serve)
- `flask_app.py` - Web server with split-view interface

**Core Processing:**
- `converter.py` - Core conversion logic from HDF5 to HTML/images
- `webplot_cli.py` - Workflow orchestration (single file, batch, parallel)
- `monitor_and_process.py` - Directory watching with producer-consumer pattern

**Visualization:**
- `plot_images.py` - Generate matplotlib plots (SAXS, stability, correlation, twotime)
- `html_utlits.py` - Jinja2 template rendering and HTML generation
- `metadata_utils.py` - Extract and format HDF5 metadata to JSON

### Data Flow

1. **Input**: HDF5 file with XPCS analysis results
2. **Load**: Read with `pyxpcsviewer.XpcsFile`
3. **Extract**: SAXS, stability, correlation, twotime data
4. **Process**: Generate plots, export to text files, extract metadata
5. **Generate**: HTML summary page with embedded plots and links
6. **Output**: Structured directory with HTML, images, data files, metadata.json

### Parallel Processing

- Uses Python's `multiprocessing` module (NOT threading) for CPU-bound tasks
- Default: 8 worker processes (configurable via `--num-workers`)
- Batch processing distributes files across worker pool
- Monitoring mode uses producer-consumer pattern with thread-safe queue

### Flask Web Server

- Factory pattern: `create_app(html_folder)` for flexible configuration
- Split-view interface: resizable panels with file browser on left, content on right
- Subdirectory navigation with automatic combined summary generation
- **Development only** - use nginx/Apache for production deployments

## CLI Command Reference

### plot - Convert HDF5 files to web format

```bash
# Single file
xpcs_webplot plot input.hdf --html-dir ./html

# Batch processing with 8 workers
xpcs_webplot plot /data/*.hdf --html-dir ./results --num-workers 8

# Real-time monitoring
xpcs_webplot plot /data/incoming --monitor --html-dir ./live

# High-quality output
xpcs_webplot plot data.hdf --dpi 600 --num-img 12 --html-dir ./publication

# Image-only mode (skip text exports)
xpcs_webplot plot data.hdf --image-only
```

**Key Options:**
- `--html-dir` - Output directory (default: `/tmp`)
- `--num-workers` - Parallel processes (default: `8`)
- `--num-img` - Number of twotime images (default: `4`)
- `--dpi` - Plot resolution (default: `240`)
- `--monitor` - Watch directory for new files
- `--overwrite` - Overwrite existing results
- `--image-only` - Skip text file exports
- `--no-save-result` - Skip data saving entirely

### combine - Create unified index

```bash
xpcs_webplot combine ./html --output combined_summary.html
```

### serve - Start web server

```bash
# Basic server
xpcs_webplot serve ./html

# Custom port and host
xpcs_webplot serve ./html --port 8080 --host 0.0.0.0

# Debug mode (development only)
xpcs_webplot serve ./html --debug
```

## Output Structure

Each conversion creates a result folder with:

```
result_folder/
├── summary.html              # Main page with plots and metadata
├── metadata.json            # Extracted HDF5 metadata
├── images/                  # Optional subdirectory (--no-create-image-directory to disable)
│   ├── saxs.png
│   ├── stability.png
│   ├── g2_multitau.png
│   └── twotime_*.png
├── data/                    # Data files (if --save-result enabled)
│   ├── saxs_1d.txt
│   ├── saxs_2d.tif
│   ├── g2.txt
│   └── c2_*.tif
```

## Design Patterns

**Factory Pattern**: `create_app(html_folder)` in `flask_app.py` for Flask instantiation

**Producer-Consumer**: File monitoring uses watchdog observer (producer) feeding multiprocessing pool (consumer) via thread-safe queue

**Wrapper Pattern**: `convert_xpcs_result_safe()` wraps conversion with exception handling to prevent batch processing failures

**Template Method**: Standard conversion workflow with customizable steps via options

## Important Conventions

### Dependencies

- Uses `pyxpcsviewer` (imported as `XpcsFile`) for reading XPCS HDF5 files
- Core stack: numpy, h5py, matplotlib, jinja2, flask, watchdog
- Templates in `src/xpcs_webplot/templates/` are included via package data

### Error Handling

- Conversions use safe wrappers to log errors without stopping batch jobs
- Failed files are logged with detailed error messages
- Partial results are saved when possible

### Configuration

- All settings via CLI arguments (no environment variables)
- Defaults defined in `pyproject.toml` for pytest, black, isort, mypy
- No config files for the application itself

### CLI Argument Migration Note

Recent changes renamed arguments for clarity:
- `--target-dir` → `--html-dir`
- `--num-processes` → `--num-workers`

Old arguments may still exist in older documentation.
