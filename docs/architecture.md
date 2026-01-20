# Architecture

This document describes the system architecture and design decisions for XPCS WebPlot.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Module Organization](#module-organization)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)

## Overview

XPCS WebPlot is designed as a modular Python package for converting X-ray Photon Correlation Spectroscopy (XPCS) analysis results into web-viewable formats. The architecture emphasizes:

- **Modularity**: Clear separation of concerns across modules
- **Scalability**: Parallel processing for batch operations
- **Flexibility**: Multiple interfaces (CLI, programmatic, web)
- **Robustness**: Error handling and recovery mechanisms

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
├─────────────────┬──────────────────┬────────────────────────┤
│   CLI (cli.py)  │  Web (flask_app) │  Programmatic (API)    │
└────────┬────────┴────────┬─────────┴──────────┬─────────────┘
         │                 │                     │
         └─────────────────┼─────────────────────┘
                           │
         ┌─────────────────▼─────────────────────┐
         │      Core Processing Layer             │
         ├────────────────────────────────────────┤
         │  • converter.py (conversion logic)     │
         │  • webplot_cli.py (workflow mgmt)      │
         │  • monitor_and_process.py (watching)   │
         └────────────────┬───────────────────────┘
                          │
         ┌────────────────▼───────────────────────┐
         │      Visualization Layer               │
         ├────────────────────────────────────────┤
         │  • plot_images.py (plotting)           │
         │  • html_utlits.py (HTML generation)    │
         │  • metadata_utils.py (data extraction) │
         └────────────────┬───────────────────────┘
                          │
         ┌────────────────▼───────────────────────┐
         │      Data Layer                        │
         ├────────────────────────────────────────┤
         │  • pyxpcsviewer (HDF5 reading)         │
         │  • File system (output storage)        │
         └────────────────────────────────────────┘
```

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         XPCS WebPlot                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    CLI      │  │  Flask App   │  │  Monitoring  │        │
│  │  Interface  │  │   (Web UI)   │  │   Service    │        │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                │                  │                 │
│         └────────────────┼──────────────────┘                 │
│                          │                                    │
│         ┌────────────────▼────────────────┐                  │
│         │   Conversion Orchestrator       │                  │
│         │   (webplot_cli.py)              │                  │
│         └────────────────┬────────────────┘                  │
│                          │                                    │
│         ┌────────────────▼────────────────┐                  │
│         │   Core Converter                │                  │
│         │   (converter.py)                │                  │
│         └────┬──────────────┬─────────────┘                  │
│              │              │                                 │
│    ┌─────────▼────┐  ┌─────▼──────────┐                     │
│    │   Plotting   │  │  HTML/Metadata │                     │
│    │   Engine     │  │   Generator    │                     │
│    └──────────────┘  └────────────────┘                     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Module Organization

### Core Modules

#### cli.py
- **Purpose**: Command-line interface entry point
- **Responsibilities**:
  - Argument parsing with argparse
  - Subcommand routing (plot, combine, serve)
  - User input validation
  - Error reporting

#### converter.py
- **Purpose**: Core conversion logic
- **Responsibilities**:
  - HDF5 file reading via pyxpcsviewer
  - Data extraction and transformation
  - Orchestrating plot generation
  - File output management
  - Error handling and recovery

#### webplot_cli.py
- **Purpose**: High-level workflow management
- **Responsibilities**:
  - Single file conversion workflow
  - Batch processing coordination
  - Multiprocessing pool management
  - Progress tracking

### Visualization Modules

#### plot_images.py
- **Purpose**: Generate plots from XPCS data
- **Responsibilities**:
  - SAXS pattern visualization
  - Stability analysis plots
  - Correlation function plots
  - Twotime correlation maps
  - Plot styling and formatting

#### html_utlits.py
- **Purpose**: HTML generation and manipulation
- **Responsibilities**:
  - Jinja2 template rendering
  - Summary page generation
  - Combined index creation
  - Metadata embedding

#### metadata_utils.py
- **Purpose**: Metadata extraction and formatting
- **Responsibilities**:
  - Extract metadata from HDF5 files
  - Convert to JSON-serializable format
  - Type conversion (numpy → Python)
  - Metadata validation

### Service Modules

#### flask_app.py
- **Purpose**: Web server for result viewing
- **Responsibilities**:
  - Flask application factory
  - Route definitions
  - Template rendering
  - Static file serving
  - Subdirectory navigation
  - API endpoints

#### monitor_and_process.py
- **Purpose**: Directory monitoring and auto-processing
- **Responsibilities**:
  - File system watching (watchdog)
  - Producer-consumer queue management
  - Multiprocessing coordination
  - Event handling

## Data Flow

### Conversion Pipeline

```
Input HDF5 File
      │
      ▼
┌─────────────────┐
│ Load with       │
│ pyxpcsviewer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Data    │
│ • SAXS          │
│ • Stability     │
│ • Correlation   │
│ • Twotime       │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌──────────┐
   │Generate │   │ Export   │   │ Extract  │
   │ Plots   │   │ to Text  │   │Metadata  │
   └────┬────┘   └────┬─────┘   └────┬─────┘
        │             │              │
        └─────────────┼──────────────┘
                      ▼
              ┌──────────────┐
              │ Generate     │
              │ HTML Summary │
              └──────┬───────┘
                     │
                     ▼
              Output Directory
```

### Batch Processing Flow

```
File List
    │
    ▼
┌───────────────────┐
│ Create Process    │
│ Pool (N workers)  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Distribute Files  │
│ to Workers        │
└────────┬──────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│Worker 1││Worker 2││Worker 3││Worker N│
│Convert ││Convert ││Convert ││Convert │
└───┬────┘└───┬────┘└───┬────┘└───┬────┘
    │         │         │         │
    └─────────┴─────────┴─────────┘
                  │
                  ▼
          ┌──────────────┐
          │ Collect      │
          │ Results      │
          └──────────────┘
```

### Monitoring Flow

```
Directory to Monitor
         │
         ▼
┌─────────────────────┐
│ Watchdog Observer   │
│ (File System Events)│
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Event Filter │
    │ (*.hdf only) │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Thread-Safe  │
    │    Queue     │
    └──────┬───────┘
           │
           ▼
┌──────────────────────┐
│ Consumer Processes   │
│ (Process Pool)       │
└──────────┬───────────┘
           │
           ▼
    Output Directory
```

## Design Patterns

### Factory Pattern

Used in `flask_app.py` for creating Flask applications:

```python
def create_app(html_folder='html'):
    """Factory function to create Flask app"""
    app = Flask(__name__)
    # Configure app with html_folder
    # Register routes
    return app
```

**Benefits**:
- Allows multiple app instances with different configurations
- Facilitates testing with different settings
- Enables dynamic configuration

### Producer-Consumer Pattern

Used in `monitor_and_process.py` for file monitoring:

```python
# Producer: Watchdog observer adds files to queue
# Consumer: Process pool workers take files from queue

queue = Queue()

# Producer thread
observer.schedule(handler, path)
handler.on_created = lambda event: queue.put(event.src_path)

# Consumer processes
with Pool(num_processes) as pool:
    while True:
        file_path = queue.get()
        pool.apply_async(convert_file, (file_path,))
```

**Benefits**:
- Decouples file detection from processing
- Enables parallel processing
- Handles variable processing times

### Wrapper Pattern

Used for error handling in `converter.py`:

```python
def convert_xpcs_result_safe(*args, **kwargs):
    """Safe wrapper with exception handling"""
    try:
        return convert_xpcs_result(*args, **kwargs)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False
```

**Benefits**:
- Prevents crashes in batch processing
- Centralizes error handling
- Maintains consistent interface

### Template Method Pattern

Used in conversion workflow:

```python
def convert_xpcs_result(fname, **options):
    # Template method defining conversion steps
    xf = load_file(fname)
    save_data(xf)      # Optional step
    generate_plots(xf)  # Required step
    create_html(xf)     # Optional step
```

**Benefits**:
- Defines standard workflow
- Allows customization via options
- Ensures consistency

## Technology Stack

### Core Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| Python | Runtime | ≥3.8 |
| numpy | Numerical operations | Latest |
| h5py | HDF5 file I/O | Latest |
| matplotlib | Plotting | Latest |
| jinja2 | HTML templating | Latest |
| flask | Web framework | Latest |
| watchdog | File system monitoring | Latest |
| pyxpcsviewer | XPCS file reading | Latest |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| pytest | Testing framework |
| pytest-cov | Coverage reporting |
| black | Code formatting |
| flake8 | Linting |
| mypy | Type checking |

### Build System

- **Build backend**: setuptools
- **Configuration**: pyproject.toml (PEP 517/518)
- **Package structure**: src layout

## Design Decisions

### Why src Layout?

**Decision**: Use `src/xpcs_webplot/` instead of `xpcs_webplot/`

**Rationale**:
- Prevents accidental imports of uninstalled package
- Ensures tests run against installed version
- Follows modern Python packaging best practices
- Better isolation between source and installed code

### Why pyproject.toml?

**Decision**: Use `pyproject.toml` instead of `setup.py`

**Rationale**:
- Modern standard (PEP 517/518)
- Single configuration file for all tools
- Better dependency resolution
- Declarative instead of imperative

### Why Multiprocessing?

**Decision**: Use multiprocessing instead of threading

**Rationale**:
- CPU-bound operations (plotting, data processing)
- Bypasses Python GIL limitations
- Better performance on multi-core systems
- Process isolation for robustness

### Why Flask Development Server?

**Decision**: Include Flask dev server, recommend nginx for production

**Rationale**:
- Easy setup for development and testing
- Good enough for small-scale deployments
- Clear upgrade path to production servers
- Familiar to Python developers

### Why Jinja2 Templates?

**Decision**: Use Jinja2 for HTML generation

**Rationale**:
- Powerful templating with inheritance
- Well-integrated with Flask
- Separates presentation from logic
- Widely used and documented

### Why Watchdog for Monitoring?

**Decision**: Use watchdog library for file system monitoring

**Rationale**:
- Cross-platform compatibility
- Efficient event-based monitoring
- Well-maintained and reliable
- Simple API

### Why NumPy Docstrings?

**Decision**: Use NumPy-style docstrings

**Rationale**:
- Standard in scientific Python community
- Well-structured and readable
- Supported by documentation generators
- Familiar to target users

## Performance Considerations

### Parallel Processing

- Default: 4 processes
- Configurable via `--num-processes`
- Optimal value depends on:
  - Number of CPU cores
  - Available memory
  - I/O characteristics

### Memory Management

- Process files one at a time in each worker
- Close HDF5 files after reading
- Clear matplotlib figures after saving
- Avoid loading entire datasets into memory

### I/O Optimization

- Batch file operations where possible
- Use buffered I/O for text exports
- Minimize HDF5 file reopening
- Cache metadata when appropriate

## Extensibility

### Adding New Plot Types

1. Add function to `plot_images.py`
2. Call from `plot_xpcs_result()` in `converter.py`
3. Update HTML template to display new plot

### Adding New Export Formats

1. Add export function to `converter.py`
2. Call from `save_xpcs_result()`
3. Update documentation

### Adding New CLI Commands

1. Add subparser in `cli.py`
2. Implement handler function
3. Update help text and documentation

### Customizing Web Interface

1. Modify templates in `src/xpcs_webplot/templates/`
2. Add routes in `flask_app.py`
3. Update static assets if needed

## Security Considerations

### File System Access

- Validate all file paths
- Prevent directory traversal attacks
- Use absolute paths internally
- Sanitize user inputs

### Web Server

- Don't use Flask dev server in production
- Validate all user inputs
- Sanitize file paths in routes
- Use proper HTTP headers

### Data Privacy

- No authentication/authorization built-in
- Assumes trusted network environment
- Consider adding auth for production use
- Be careful with sensitive data

## Future Enhancements

### Planned Features

1. **Database Backend**: Store metadata in SQLite/PostgreSQL
2. **REST API**: Programmatic access to results
3. **Real-time Updates**: WebSocket support for live monitoring
4. **Advanced Filtering**: More sophisticated result filtering
5. **Export Formats**: PDF reports, CSV exports
6. **Comparison Tools**: Side-by-side result comparison

### Architectural Improvements

1. **Plugin System**: Allow third-party extensions
2. **Caching Layer**: Cache expensive computations
3. **Async Processing**: Use asyncio for I/O operations
4. **Configuration Files**: Support config files for defaults
5. **Logging Improvements**: Structured logging with levels

## See Also

- [API Reference](api_reference.md) - Detailed API documentation
- [Development Guide](development_guide.md) - Contributing guidelines
- [User Guide](user_guide.md) - Usage instructions
