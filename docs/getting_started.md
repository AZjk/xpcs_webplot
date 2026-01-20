# Getting Started with XPCS WebPlot

This guide will help you get started with XPCS WebPlot quickly.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Next Steps](#next-steps)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/AZjk/xpcs_webplot.git
cd xpcs_webplot

# Install in development mode
pip install -e ".[dev]"
```

### Install for Users

```bash
# Install from PyPI (when available)
pip install xpcs_webplot

# Or install from source without dev dependencies
pip install .
```

### Verify Installation

```bash
# Check that the command is available
xpcs_webplot --help
```

You should see the help message with available subcommands.

## Quick Start

### Convert a Single XPCS File

The most basic operation is converting a single XPCS HDF5 file to web format:

```bash
xpcs_webplot plot /path/to/your/xpcs_file.hdf
```

This will:
- Read the XPCS analysis results from the HDF5 file
- Generate plots (SAXS, stability, correlation functions)
- Export data to text files
- Create an HTML summary page
- Save everything to `./html/` directory by default

### View Results in Browser

Start the Flask web server to view your results:

```bash
xpcs_webplot serve ./html
```

Then open your browser to `http://localhost:5000` to view the interactive results.

### Process Multiple Files

To process all XPCS files in a directory:

```bash
xpcs_webplot plot /path/to/directory/*.hdf --target-dir ./html
```

### Combine Results

After processing multiple files, combine them into a single index page:

```bash
xpcs_webplot combine ./html
```

## Basic Usage

### The `plot` Subcommand

Convert XPCS HDF files to web format:

```bash
# Basic usage
xpcs_webplot plot input.hdf

# Specify output directory
xpcs_webplot plot input.hdf --target-dir ./output

# Process with custom settings
xpcs_webplot plot input.hdf --num-img 8 --dpi 300

# Overwrite existing results
xpcs_webplot plot input.hdf --overwrite

# Generate only images (no data export)
xpcs_webplot plot input.hdf --image-only

# Skip saving result files
xpcs_webplot plot input.hdf --no-save-result
```

### The `combine` Subcommand

Combine multiple result folders into a single index:

```bash
# Combine all results in a directory
xpcs_webplot combine ./html

# Specify output filename
xpcs_webplot combine ./html --output combined_index.html
```

### The `serve` Subcommand

Start a web server to browse results:

```bash
# Start server on default port (5000)
xpcs_webplot serve ./html

# Specify custom port and host
xpcs_webplot serve ./html --port 8080 --host 0.0.0.0

# Enable debug mode
xpcs_webplot serve ./html --debug
```

## Common Workflows

### Workflow 1: Single File Analysis

```bash
# 1. Convert the file
xpcs_webplot plot data.hdf

# 2. View results
xpcs_webplot serve ./html
```

### Workflow 2: Batch Processing

```bash
# 1. Process all files in a directory
xpcs_webplot plot /data/experiment/*.hdf --target-dir ./results

# 2. Combine results
xpcs_webplot combine ./results

# 3. Serve results
xpcs_webplot serve ./results
```

### Workflow 3: Real-time Monitoring

```bash
# Monitor a directory and auto-process new files
xpcs_webplot plot /data/incoming --monitor --target-dir ./results
```

This will watch the directory and automatically process new HDF files as they appear.

## Understanding the Output

After running `xpcs_webplot plot`, you'll find the following structure:

```
html/
└── your_file_name/
    ├── summary.html          # Main summary page
    ├── metadata.json         # Extracted metadata
    ├── saxs.png             # SAXS pattern plot
    ├── stability.png        # Stability analysis plot
    ├── g2_multitau.png      # Multitau correlation plot
    ├── twotime_*.png        # Twotime correlation maps
    ├── c2_saxs.txt          # SAXS data
    ├── c2_g2.txt            # G2 correlation data
    ├── c2_stability.txt     # Stability data
    └── c2_twotime_*.txt     # Twotime data
```

## Next Steps

Now that you have the basics, explore more advanced features:

- Read the [User Guide](user_guide.md) for detailed documentation
- Check the [API Reference](api_reference.md) for programmatic usage
- See the [Development Guide](development_guide.md) to contribute
- Review [Deployment Guide](deployment_guide.md) for production setup

## Getting Help

If you run into issues:

1. Check the [FAQ](faq.md)
2. Review the error messages carefully
3. Enable verbose logging with `--verbose` flag (if available)
4. Search or create an issue on [GitHub](https://github.com/AZjk/xpcs_webplot/issues)
