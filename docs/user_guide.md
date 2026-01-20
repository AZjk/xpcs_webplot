# User Guide

This comprehensive guide covers all features and commands available in XPCS WebPlot.

## Table of Contents

- [Command-Line Interface](#command-line-interface)
- [Plot Subcommand](#plot-subcommand)
- [Combine Subcommand](#combine-subcommand)
- [Serve Subcommand](#serve-subcommand)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)

## Command-Line Interface

XPCS WebPlot provides a main command `xpcs_webplot` with three subcommands:

```bash
xpcs_webplot <subcommand> [options]
```

### Available Subcommands

- **`plot`** - Convert XPCS HDF files to web-viewable format with plots and data exports
- **`combine`** - Combine multiple result folders into a unified index page
- **`serve`** - Start Flask web server to browse and view results interactively

## Plot Subcommand

The `plot` subcommand converts XPCS HDF5 analysis files into web-viewable formats.

### Basic Syntax

```bash
xpcs_webplot plot <input_files> [options]
```

### Input Specification

You can specify input files in several ways:

```bash
# Single file
xpcs_webplot plot data.hdf

# Multiple files
xpcs_webplot plot file1.hdf file2.hdf file3.hdf

# Wildcard patterns
xpcs_webplot plot /data/*.hdf

# Directory (processes all .hdf files)
xpcs_webplot plot /data/experiment/
```

### Options

#### `--target-dir` (default: `./html`)

Specify the output directory for generated HTML and plots:

```bash
xpcs_webplot plot data.hdf --target-dir ./results
```

#### `--num-img` (default: `4`)

Number of twotime correlation images to generate:

```bash
xpcs_webplot plot data.hdf --num-img 8
```

#### `--dpi` (default: `240`)

Resolution (dots per inch) for generated plots:

```bash
xpcs_webplot plot data.hdf --dpi 300
```

#### `--overwrite` (default: `False`)

Overwrite existing results if they already exist:

```bash
xpcs_webplot plot data.hdf --overwrite
```

#### `--image-only` (default: `False`)

Generate only image files, skip data export to text files:

```bash
xpcs_webplot plot data.hdf --image-only
```

#### `--no-create-image-directory` (default: creates directory)

Skip creating an 'images' subdirectory within each result folder:

```bash
xpcs_webplot plot data.hdf --no-create-image-directory
```

#### `--save-result` / `--no-save-result` (default: `True`)

Control whether to save result data to text files:

```bash
# Skip saving text files
xpcs_webplot plot data.hdf --no-save-result

# Explicitly enable (default behavior)
xpcs_webplot plot data.hdf --save-result
```

#### `--monitor` (default: `False`)

Enable real-time directory monitoring for new files:

```bash
xpcs_webplot plot /data/incoming --monitor --target-dir ./results
```

When enabled, the program will:
- Watch the input directory for new HDF files
- Automatically process new files as they appear
- Continue running until manually stopped (Ctrl+C)

#### `--num-processes` (default: `4`)

Number of parallel processes for batch processing:

```bash
xpcs_webplot plot /data/*.hdf --num-processes 8
```

### Examples

#### Example 1: Basic Conversion

```bash
xpcs_webplot plot experiment_001.hdf
```

Creates output in `./html/experiment_001/` with:
- HTML summary page
- SAXS, stability, and correlation plots
- Exported data files

#### Example 2: High-Quality Output

```bash
xpcs_webplot plot data.hdf --dpi 600 --num-img 12 --target-dir ./publication
```

Generates high-resolution plots suitable for publication.

#### Example 3: Batch Processing

```bash
xpcs_webplot plot /data/2024_01/*.hdf --target-dir ./results --num-processes 8
```

Processes all HDF files in parallel using 8 CPU cores.

#### Example 4: Monitoring Mode

```bash
xpcs_webplot plot /data/live --monitor --target-dir ./live_results
```

Continuously monitors `/data/live` and processes new files automatically.

## Combine Subcommand

The `combine` subcommand creates a unified index page from multiple result folders.

### Basic Syntax

```bash
xpcs_webplot combine <html_folder> [options]
```

### Options

#### `--output` (default: `combined_summary.html`)

Specify the output filename for the combined index:

```bash
xpcs_webplot combine ./html --output index.html
```

### How It Works

The combine command:
1. Scans the specified directory for result folders
2. Extracts metadata from each `summary.html` file
3. Creates a unified index page with:
   - Sortable table of all results
   - Links to individual result pages
   - Summary statistics
   - Filtering capabilities

### Examples

#### Example 1: Basic Combine

```bash
xpcs_webplot combine ./html
```

Creates `./html/combined_summary.html` with all results.

#### Example 2: Custom Output

```bash
xpcs_webplot combine ./results --output master_index.html
```

Creates `./results/master_index.html`.

## Serve Subcommand

The `serve` subcommand starts a Flask web server for interactive result browsing.

### Basic Syntax

```bash
xpcs_webplot serve <html_folder> [options]
```

### Options

#### `--port` (default: `5000`)

Specify the port number for the web server:

```bash
xpcs_webplot serve ./html --port 8080
```

#### `--host` (default: `0.0.0.0`)

Specify the host address to bind to:

```bash
# Localhost only
xpcs_webplot serve ./html --host 127.0.0.1

# All network interfaces (default)
xpcs_webplot serve ./html --host 0.0.0.0
```

#### `--debug` (default: `False`)

Enable Flask debug mode for development:

```bash
xpcs_webplot serve ./html --debug
```

**Warning**: Never use debug mode in production!

### Features

The web server provides:

- **Interactive Index**: Browse all results with filtering and sorting
- **Subdirectory Support**: Navigate through nested result structures
- **Combined Views**: View multiple results in a single page
- **Direct File Access**: Access individual plots and data files
- **Responsive Design**: Works on desktop and mobile devices

### Examples

#### Example 1: Basic Server

```bash
xpcs_webplot serve ./html
```

Access at `http://localhost:5000`

#### Example 2: Custom Port

```bash
xpcs_webplot serve ./html --port 8080
```

Access at `http://localhost:8080`

#### Example 3: Network Access

```bash
xpcs_webplot serve ./html --host 0.0.0.0 --port 80
```

Access from any computer on the network at `http://<your-ip-address>`

## Configuration

### Environment Variables

Currently, XPCS WebPlot does not use environment variables for configuration. All settings are passed via command-line arguments.

### Default Settings

Default values for common options:

| Option | Default | Description |
|--------|---------|-------------|
| `target-dir` | `./html` | Output directory |
| `num-img` | `4` | Number of twotime images |
| `dpi` | `240` | Plot resolution |
| `num-processes` | `4` | Parallel processes |
| `port` | `5000` | Web server port |
| `host` | `0.0.0.0` | Web server host |

## Advanced Features

### Real-Time Monitoring

The monitoring feature uses a producer-consumer architecture:

- **Producer**: Watches directory for new files using `watchdog`
- **Consumer**: Processes files from a queue using multiprocessing
- **Queue**: Thread-safe queue for file paths

```bash
xpcs_webplot plot /data/incoming --monitor --num-processes 4
```

### Subdirectory Organization

The serve command supports hierarchical result organization:

```
html/
├── experiment_A/
│   ├── sample_001/
│   └── sample_002/
└── experiment_B/
    ├── sample_003/
    └── sample_004/
```

The web interface will:
- Show subdirectories at the root level
- Allow navigation into subdirectories
- Display combined summaries for each subdirectory

### Parallel Processing

Batch processing uses Python's multiprocessing:

```bash
# Use all available CPU cores
xpcs_webplot plot /data/*.hdf --num-processes $(nproc)
```

### Error Handling

The converter includes robust error handling:

- Failed conversions are logged but don't stop batch processing
- Detailed error messages help diagnose issues
- Partial results are saved when possible

### Output Structure

Each result folder contains:

```
result_folder/
├── summary.html              # Main summary page
├── metadata.json            # Extracted metadata
├── images/                  # Optional subdirectory
│   ├── saxs.png
│   ├── stability.png
│   ├── g2_multitau.png
│   └── twotime_*.png
├── c2_saxs.txt              # SAXS data
├── c2_g2.txt                # G2 correlation
├── c2_stability.txt         # Stability data
├── c2_twotime_*.txt         # Twotime data
└── c2_g2_partials.txt       # Partial G2 data
```

## Tips and Best Practices

### Performance Optimization

1. **Use parallel processing** for batch jobs:
   ```bash
   xpcs_webplot plot /data/*.hdf --num-processes 8
   ```

2. **Adjust DPI** based on needs:
   - Quick preview: `--dpi 120`
   - Standard: `--dpi 240` (default)
   - Publication: `--dpi 600`

3. **Use `--image-only`** when you don't need text exports:
   ```bash
   xpcs_webplot plot data.hdf --image-only
   ```

### Workflow Recommendations

1. **Development**: Use `--debug` with serve command
2. **Production**: Use proper web server (nginx, Apache) instead of Flask dev server
3. **Archival**: Use high DPI and save all data
4. **Quick checks**: Use `--image-only` and lower DPI

### Troubleshooting

Common issues and solutions:

1. **Out of memory**: Reduce `--num-processes`
2. **Slow processing**: Increase `--num-processes`
3. **Large output**: Use `--image-only` or `--no-save-result`
4. **Port in use**: Change `--port` to different value

## See Also

- [API Reference](api_reference.md) - Programmatic usage
- [Architecture](architecture.md) - System design
- [FAQ](faq.md) - Common questions
