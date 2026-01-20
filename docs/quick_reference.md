# Quick Reference

Quick reference guide for common XPCS WebPlot commands and options.

## Installation

```bash
# Install from source
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Basic Commands

### Convert Single File

```bash
xpcs_webplot plot input.hdf
```

### Convert Multiple Files

```bash
xpcs_webplot plot /path/to/*.hdf
```

### Combine Results

```bash
xpcs_webplot combine ./html
```

### Start Web Server

```bash
xpcs_webplot serve ./html
```

## Common Options

### Plot Command

| Option | Default | Description |
|--------|---------|-------------|
| `--target-dir` | `./html` | Output directory |
| `--num-img` | `4` | Number of twotime images |
| `--dpi` | `240` | Plot resolution |
| `--overwrite` | `False` | Overwrite existing results |
| `--image-only` | `False` | Skip data export |
| `--no-save-result` | - | Skip saving text files |
| `--monitor` | `False` | Watch directory for new files |
| `--num-processes` | `4` | Parallel processes |

### Serve Command

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `5000` | Server port |
| `--host` | `0.0.0.0` | Server host |
| `--debug` | `False` | Debug mode (dev only) |

## Usage Examples

### Quick Preview

```bash
xpcs_webplot plot data.hdf --dpi 120 --num-img 2 --image-only
xpcs_webplot serve ./html
```

### High Quality

```bash
xpcs_webplot plot data.hdf --dpi 600 --num-img 12
```

### Batch Processing

```bash
xpcs_webplot plot /data/*.hdf --num-processes 8 --target-dir ./results
xpcs_webplot combine ./results
```

### Monitoring

```bash
xpcs_webplot plot /data/incoming --monitor --target-dir ./live
```

### Custom Server

```bash
xpcs_webplot serve ./html --port 8080 --host 127.0.0.1
```

## Output Structure

```
html/
└── result_name/
    ├── summary.html          # Main page
    ├── metadata.json         # Metadata
    ├── saxs.png             # SAXS plot
    ├── stability.png        # Stability plot
    ├── g2_multitau.png      # G2 plot
    ├── twotime_*.png        # Twotime plots
    ├── c2_saxs.txt          # SAXS data
    ├── c2_g2.txt            # G2 data
    ├── c2_stability.txt     # Stability data
    └── c2_twotime_*.txt     # Twotime data
```

## Programmatic Usage

### Basic Conversion

```python
from xpcs_webplot.converter import convert_xpcs_result

convert_xpcs_result('data.hdf', target_dir='output')
```

### Batch Processing

```python
from xpcs_webplot.webplot_cli import convert_many_files
import glob

files = glob.glob('/data/*.hdf')
convert_many_files(files, num_processes=8)
```

### Custom Flask App

```python
from xpcs_webplot.flask_app import create_app

app = create_app('my_results')
app.run(host='0.0.0.0', port=5000)
```

## Troubleshooting

### Command Not Found

```bash
pip install -e .
export PATH="$HOME/.local/bin:$PATH"
```

### Port Already in Use

```bash
xpcs_webplot serve ./html --port 8080
```

### Slow Processing

```bash
xpcs_webplot plot /data/*.hdf --num-processes 8 --dpi 120
```

### Out of Memory

```bash
xpcs_webplot plot /data/*.hdf --num-processes 2
```

## File Locations

| Item | Location |
|------|----------|
| Source code | `src/xpcs_webplot/` |
| Templates | `src/xpcs_webplot/templates/` |
| Tests | `tests/` |
| Documentation | `docs/` |
| Configuration | `pyproject.toml` |

## Key Modules

| Module | Purpose |
|--------|---------|
| `cli.py` | Command-line interface |
| `converter.py` | Core conversion logic |
| `flask_app.py` | Web server |
| `plot_images.py` | Plotting functions |
| `html_utlits.py` | HTML generation |
| `monitor_and_process.py` | Directory monitoring |

## Environment Variables

Currently, XPCS WebPlot does not use environment variables. All configuration is via command-line arguments.

## Keyboard Shortcuts

### In Monitoring Mode

- `Ctrl+C` - Stop monitoring

### In Web Browser

- Standard browser shortcuts apply

## URLs

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/AZjk/xpcs_webplot |
| PyPI | https://pypi.python.org/pypi/xpcs_webplot |
| Issues | https://github.com/AZjk/xpcs_webplot/issues |
| Docs | https://xpcs-webplot.readthedocs.io |

## Getting Help

1. Check [FAQ](faq.md)
2. Read [User Guide](user_guide.md)
3. Search [GitHub Issues](https://github.com/AZjk/xpcs_webplot/issues)
4. Create new issue

## See Full Documentation

- [Getting Started](getting_started.md) - Installation and basics
- [User Guide](user_guide.md) - Complete usage guide
- [API Reference](api_reference.md) - API documentation
- [Architecture](architecture.md) - System design
- [Development Guide](development_guide.md) - Contributing
- [Deployment Guide](deployment_guide.md) - Production setup
- [FAQ](faq.md) - Common questions
