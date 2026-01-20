# API Reference

Complete API documentation for all modules in the XPCS WebPlot package.

## Table of Contents

- [Module Overview](#module-overview)
- [cli Module](#cli-module)
- [converter Module](#converter-module)
- [webplot_cli Module](#webplot_cli-module)
- [flask_app Module](#flask_app-module)
- [plot_images Module](#plot_images-module)
- [html_utlits Module](#html_utlits-module)
- [monitor_and_process Module](#monitor_and_process-module)
- [metadata_utils Module](#metadata_utils-module)

## Module Overview

The XPCS WebPlot package consists of several modules:

| Module | Purpose |
|--------|---------|
| `cli` | Command-line interface entry point |
| `converter` | Core conversion logic for XPCS files |
| `webplot_cli` | High-level conversion functions |
| `flask_app` | Flask web server for result viewing |
| `plot_images` | Plotting functions for XPCS data |
| `html_utlits` | HTML generation utilities |
| `monitor_and_process` | Directory monitoring and batch processing |
| `metadata_utils` | Metadata extraction and formatting |

## cli Module

**Location**: `src/xpcs_webplot/cli.py`

Main entry point for the command-line interface.

### Functions

#### `main()`

Main entry point for the XPCS webplot command-line interface.

**Returns:**
- `int`: Exit code (0 for success, 1 for error)

**Description:**

Provides a command-line interface with three subcommands:
- `plot`: Convert XPCS HDF files to web-viewable format
- `combine`: Combine multiple result folders into unified index
- `serve`: Start Flask web server for interactive browsing

**Example:**

```python
import sys
from xpcs_webplot.cli import main

if __name__ == "__main__":
    sys.exit(main())
```

#### `run_flask_server(html_folder=".", port=5000, host="0.0.0.0")`

Start Flask web server to serve XPCS webplot results.

**Parameters:**
- `html_folder` (str): Path to directory containing HTML results
- `port` (int): Port number for web server (default: 5000)
- `host` (str): Host address to bind to (default: "0.0.0.0")

**Description:**

Launches a Flask development server that provides a web interface for browsing and viewing XPCS analysis results.

**Example:**

```python
from xpcs_webplot.cli import run_flask_server

run_flask_server('html', port=8080, host='127.0.0.1')
```

## converter Module

**Location**: `src/xpcs_webplot/converter.py`

Core conversion logic for processing XPCS HDF5 files.

### Functions

#### `convert_xpcs_result(fname=None, target_dir="html", num_img=4, dpi=240, overwrite=False, image_only=False, create_image_directory=True, save_result=True)`

Convert XPCS HDF file to web-viewable format with plots and data exports.

**Parameters:**
- `fname` (str or Path): Path to input XPCS HDF file
- `target_dir` (str or Path): Output directory for results (default: "html")
- `num_img` (int): Number of twotime correlation images (default: 4)
- `dpi` (int): Resolution for plots in dots per inch (default: 240)
- `overwrite` (bool): Overwrite existing results (default: False)
- `image_only` (bool): Generate only images, skip data export (default: False)
- `create_image_directory` (bool): Create 'images' subdirectory (default: True)
- `save_result` (bool): Save data to text files (default: True)

**Returns:**
- `bool`: True if conversion successful, False otherwise

**Raises:**
- `FileNotFoundError`: If input file doesn't exist
- `ValueError`: If file format is invalid

**Example:**

```python
from xpcs_webplot.converter import convert_xpcs_result

# Basic conversion
convert_xpcs_result('data.hdf', target_dir='output')

# High-quality output
convert_xpcs_result('data.hdf', dpi=600, num_img=12)

# Images only
convert_xpcs_result('data.hdf', image_only=True)
```

#### `save_xpcs_result(xf_obj, top_dir)`

Save XPCS analysis results to text and image files.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object from pyxpcsviewer
- `top_dir` (Path): Output directory for saved files

**Description:**

Exports SAXS data, correlation functions, and twotime analysis results from an XPCS file object to a structured directory format.

**Output Files:**
- `c2_saxs.txt`: SAXS intensity data
- `c2_g2.txt`: G2 correlation function
- `c2_stability.txt`: Stability analysis data
- `c2_twotime_*.txt`: Twotime correlation maps
- `c2_g2_partials.txt`: Segmented g2 from twotime analysis

**Example:**

```python
from pyxpcsviewer.xpcs_file import XpcsFile
from xpcs_webplot.converter import save_xpcs_result
from pathlib import Path

xf = XpcsFile('data.hdf')
save_xpcs_result(xf, Path('output'))
```

#### `plot_xpcs_result(xf_obj, top_dir, num_img=4, dpi=240, image_only=False)`

Generate plots and HTML summary from XPCS file object.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `num_img` (int): Number of twotime images (default: 4)
- `dpi` (int): Plot resolution (default: 240)
- `image_only` (bool): Skip HTML generation (default: False)

**Description:**

Creates visualization plots for SAXS patterns, stability analysis, and correlation functions, then generates an HTML summary page.

**Example:**

```python
from pyxpcsviewer.xpcs_file import XpcsFile
from xpcs_webplot.converter import plot_xpcs_result
from pathlib import Path

xf = XpcsFile('data.hdf')
plot_xpcs_result(xf, Path('output'), num_img=8, dpi=300)
```

#### `convert_xpcs_result_safe(*args, **kwargs)`

Safe wrapper for convert_xpcs_result with exception handling.

**Parameters:**
- `*args`: Positional arguments for convert_xpcs_result
- `**kwargs`: Keyword arguments for convert_xpcs_result

**Returns:**
- `bool`: True if successful, False if exception occurred

**Description:**

Catches and logs any exceptions that occur during conversion, preventing crashes in batch processing scenarios.

**Example:**

```python
from xpcs_webplot.converter import convert_xpcs_result_safe

# Safe conversion that won't crash on errors
success = convert_xpcs_result_safe('data.hdf', target_dir='output')
if not success:
    print("Conversion failed, but program continues")
```

## webplot_cli Module

**Location**: `src/xpcs_webplot/webplot_cli.py`

High-level functions for file conversion workflows.

### Functions

#### `convert_one_file(fname, target_dir="html", num_img=4, dpi=240, overwrite=False, image_only=False, create_image_directory=True, save_result=True)`

Convert a single XPCS HDF file to web format.

**Parameters:**
- Same as `convert_xpcs_result`

**Returns:**
- `bool`: True if successful

**Example:**

```python
from xpcs_webplot.webplot_cli import convert_one_file

convert_one_file('experiment_001.hdf', target_dir='results')
```

#### `convert_many_files(file_list, target_dir="html", num_img=4, dpi=240, overwrite=False, image_only=False, create_image_directory=True, save_result=True, num_processes=4)`

Convert multiple XPCS files in parallel.

**Parameters:**
- `file_list` (list): List of file paths to convert
- `num_processes` (int): Number of parallel processes (default: 4)
- Other parameters same as `convert_one_file`

**Returns:**
- `list`: List of boolean results for each file

**Example:**

```python
from xpcs_webplot.webplot_cli import convert_many_files
import glob

files = glob.glob('/data/*.hdf')
results = convert_many_files(files, num_processes=8)
print(f"Successful: {sum(results)}/{len(results)}")
```

## flask_app Module

**Location**: `src/xpcs_webplot/flask_app.py`

Flask web application for serving and viewing XPCS results.

### Functions

#### `create_app(html_folder='html')`

Factory function to create Flask app with custom HTML folder.

**Parameters:**
- `html_folder` (str): Path to HTML results directory

**Returns:**
- `Flask`: Configured Flask application instance

**Example:**

```python
from xpcs_webplot.flask_app import create_app

app = create_app('my_results')
app.run(host='0.0.0.0', port=5000)
```

#### `get_html_data(html_folder, subdir=None)`

Extract metadata from all HTML folders.

**Parameters:**
- `html_folder` (str): Base HTML folder path
- `subdir` (str, optional): Subdirectory to scan within html_folder

**Returns:**
- `dict`: Dictionary with 'type', 'subdirs', and 'results' keys

**Example:**

```python
from xpcs_webplot.flask_app import get_html_data

data = get_html_data('html')
print(f"Found {len(data['results'])} results")
```

#### `get_subdirectories(html_folder)`

Get list of subdirectories that contain result folders.

**Parameters:**
- `html_folder` (str): Base HTML folder path

**Returns:**
- `list`: List of subdirectory names

**Example:**

```python
from xpcs_webplot.flask_app import get_subdirectories

subdirs = get_subdirectories('html')
for subdir in subdirs:
    print(f"Subdirectory: {subdir}")
```

## plot_images Module

**Location**: `src/xpcs_webplot/plot_images.py`

Functions for generating plots from XPCS data.

### Functions

#### `plot_crop_mask_saxs(xf_obj, top_dir, dpi=240)`

Plot SAXS pattern with crop mask overlay.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `dpi` (int): Plot resolution

**Returns:**
- `str`: Path to saved plot file

#### `plot_stability(xf_obj, top_dir, dpi=240)`

Plot stability analysis (intensity vs frame number).

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `dpi` (int): Plot resolution

**Returns:**
- `str`: Path to saved plot file

#### `plot_multitau_correlation(xf_obj, top_dir, dpi=240)`

Plot multitau correlation functions (g2 vs lag time).

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `dpi` (int): Plot resolution

**Returns:**
- `str`: Path to saved plot file

#### `plot_twotime_correlation(xf_obj, top_dir, num_img=4, dpi=240)`

Plot twotime correlation maps.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `num_img` (int): Number of images to generate
- `dpi` (int): Plot resolution

**Returns:**
- `list`: List of paths to saved plot files

## html_utlits Module

**Location**: `src/xpcs_webplot/html_utlits.py`

Utilities for HTML generation and manipulation.

### Functions

#### `convert_to_html(xf_obj, top_dir, image_dir=None)`

Generate HTML summary page from XPCS file object.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory
- `image_dir` (str, optional): Subdirectory for images

**Returns:**
- `str`: Path to generated HTML file

#### `combine_all_htmls(html_folder, output_file='combined_summary.html')`

Combine multiple result folders into unified index page.

**Parameters:**
- `html_folder` (str): Directory containing result folders
- `output_file` (str): Output filename

**Returns:**
- `str`: Path to generated combined HTML file

## monitor_and_process Module

**Location**: `src/xpcs_webplot/monitor_and_process.py`

Directory monitoring and batch processing with producer-consumer pattern.

### Functions

#### `monitor_and_process(input_path, target_dir="html", num_img=4, dpi=240, overwrite=False, image_only=False, create_image_directory=True, save_result=True, num_processes=4)`

Monitor directory for new XPCS files and process them automatically.

**Parameters:**
- `input_path` (str): Directory to monitor
- `num_processes` (int): Number of worker processes
- Other parameters same as convert_xpcs_result

**Description:**

Uses watchdog to monitor a directory for new HDF files and processes them using a producer-consumer pattern with multiprocessing.

**Example:**

```python
from xpcs_webplot.monitor_and_process import monitor_and_process

# Monitor directory and auto-process new files
monitor_and_process('/data/incoming', target_dir='results', num_processes=4)
```

## metadata_utils Module

**Location**: `src/xpcs_webplot/metadata_utils.py`

Utilities for extracting and formatting metadata.

### Functions

#### `save_metadata(xf_obj, top_dir)`

Extract and save metadata from XPCS file to JSON.

**Parameters:**
- `xf_obj` (XpcsFile): XPCS file object
- `top_dir` (Path): Output directory

**Returns:**
- `dict`: Extracted metadata dictionary

#### `convert_to_native_format(obj)`

Convert numpy/HDF5 types to native Python types for JSON serialization.

**Parameters:**
- `obj`: Object to convert

**Returns:**
- Native Python type equivalent

## Usage Examples

### Example 1: Programmatic Conversion

```python
from xpcs_webplot.converter import convert_xpcs_result
from pathlib import Path

# Convert single file
success = convert_xpcs_result(
    fname='experiment_001.hdf',
    target_dir='results',
    num_img=8,
    dpi=300,
    overwrite=True
)

if success:
    print("Conversion successful!")
```

### Example 2: Batch Processing

```python
from xpcs_webplot.webplot_cli import convert_many_files
import glob

# Get all HDF files
files = glob.glob('/data/experiment/*.hdf')

# Process in parallel
results = convert_many_files(
    files,
    target_dir='batch_results',
    num_processes=8,
    dpi=240
)

print(f"Processed {sum(results)}/{len(results)} files successfully")
```

### Example 3: Custom Flask App

```python
from xpcs_webplot.flask_app import create_app

# Create custom app
app = create_app('my_results')

# Add custom route
@app.route('/custom')
def custom_page():
    return "Custom page"

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

### Example 4: Direct Plotting

```python
from pyxpcsviewer.xpcs_file import XpcsFile
from xpcs_webplot.plot_images import (
    plot_crop_mask_saxs,
    plot_stability,
    plot_multitau_correlation
)
from pathlib import Path

# Load XPCS file
xf = XpcsFile('data.hdf')
output_dir = Path('plots')
output_dir.mkdir(exist_ok=True)

# Generate individual plots
plot_crop_mask_saxs(xf, output_dir, dpi=300)
plot_stability(xf, output_dir, dpi=300)
plot_multitau_correlation(xf, output_dir, dpi=300)
```

## See Also

- [User Guide](user_guide.md) - Command-line usage
- [Architecture](architecture.md) - System design
- [Development Guide](development_guide.md) - Contributing
