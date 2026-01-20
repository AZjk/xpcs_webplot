# Frequently Asked Questions (FAQ)

Common questions and troubleshooting tips for XPCS WebPlot.

## Table of Contents

- [General Questions](#general-questions)
- [Installation Issues](#installation-issues)
- [Usage Questions](#usage-questions)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)
- [Web Server Issues](#web-server-issues)
- [Data and Output](#data-and-output)

## General Questions

### What is XPCS WebPlot?

XPCS WebPlot is a Python package that converts X-ray Photon Correlation Spectroscopy (XPCS) analysis results from HDF5 files into interactive web-viewable formats with plots and data exports.

### What file formats does it support?

XPCS WebPlot reads HDF5 files (.hdf, .h5) that follow the XPCS analysis output format from the pyxpcsviewer package.

### Do I need to know Python to use it?

No! XPCS WebPlot provides a command-line interface that doesn't require Python programming knowledge. However, Python knowledge is helpful for advanced customization.

### Is it free?

Yes, XPCS WebPlot is open-source software released under the MIT License. It's free to use, modify, and distribute.

### Can I use it for commercial purposes?

Yes, the MIT License allows commercial use.

## Installation Issues

### I get "command not found" after installation

**Problem**: The `xpcs_webplot` command is not found.

**Solution**:
```bash
# Ensure the package is installed
pip list | grep xpcs_webplot

# If not installed, install it
pip install -e .

# Check if pip's bin directory is in PATH
which xpcs_webplot

# If not in PATH, add it (example for bash)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Installation fails with "No module named 'setuptools'"

**Problem**: Missing build dependencies.

**Solution**:
```bash
pip install --upgrade pip setuptools wheel
pip install -e .
```

### I get errors about missing dependencies

**Problem**: Required packages not installed.

**Solution**:
```bash
# Install with all dependencies
pip install -e ".[dev]"

# Or install specific missing package
pip install <package_name>
```

### Installation fails on Windows

**Problem**: Some dependencies may have issues on Windows.

**Solution**:
- Use Windows Subsystem for Linux (WSL)
- Or use Anaconda/Miniconda:
  ```bash
  conda create -n xpcs python=3.10
  conda activate xpcs
  pip install -e .
  ```

## Usage Questions

### How do I convert a single file?

```bash
xpcs_webplot plot your_file.hdf
```

The output will be in `./html/your_file/`

### How do I process multiple files?

```bash
# Using wildcards
xpcs_webplot plot /path/to/data/*.hdf

# Or specify directory
xpcs_webplot plot /path/to/data/
```

### How do I change the output directory?

```bash
xpcs_webplot plot input.hdf --target-dir /path/to/output
```

### How do I view the results?

```bash
# Start web server
xpcs_webplot serve ./html

# Then open browser to http://localhost:5000
```

### Can I process files automatically as they're created?

Yes! Use monitoring mode:

```bash
xpcs_webplot plot /data/incoming --monitor --target-dir ./results
```

This will watch the directory and process new files automatically.

### How do I stop the monitoring mode?

Press `Ctrl+C` to stop the monitoring process.

### Can I customize the plot resolution?

Yes, use the `--dpi` option:

```bash
# Higher resolution (better quality, larger files)
xpcs_webplot plot input.hdf --dpi 600

# Lower resolution (faster, smaller files)
xpcs_webplot plot input.hdf --dpi 120
```

### How do I generate more twotime images?

Use the `--num-img` option:

```bash
xpcs_webplot plot input.hdf --num-img 12
```

### Can I skip the data export and only generate images?

Yes, use the `--image-only` flag:

```bash
xpcs_webplot plot input.hdf --image-only
```

### How do I overwrite existing results?

Use the `--overwrite` flag:

```bash
xpcs_webplot plot input.hdf --overwrite
```

## Performance Issues

### Processing is very slow

**Possible causes and solutions**:

1. **Too few processes**:
   ```bash
   # Increase parallel processes
   xpcs_webplot plot /data/*.hdf --num-processes 8
   ```

2. **High DPI setting**:
   ```bash
   # Reduce DPI for faster processing
   xpcs_webplot plot input.hdf --dpi 120
   ```

3. **Large files**:
   - This is expected for large datasets
   - Consider processing in smaller batches

### The web server is slow

**Solutions**:

1. **Use production server** instead of Flask dev server:
   - See [Deployment Guide](deployment_guide.md)

2. **Reduce number of results**:
   - Archive old results
   - Split into subdirectories

3. **Enable caching** in nginx (production)

### I'm running out of memory

**Solutions**:

1. **Reduce parallel processes**:
   ```bash
   xpcs_webplot plot /data/*.hdf --num-processes 2
   ```

2. **Process files in smaller batches**

3. **Close other applications**

4. **Add more RAM to your system**

## Error Messages

### "FileNotFoundError: [Errno 2] No such file or directory"

**Problem**: Input file doesn't exist or path is wrong.

**Solution**:
- Check file path is correct
- Use absolute paths if relative paths don't work
- Verify file exists: `ls -l /path/to/file.hdf`

### "PermissionError: [Errno 13] Permission denied"

**Problem**: No permission to read input file or write to output directory.

**Solution**:
```bash
# Check permissions
ls -l input.hdf
ls -ld output_directory

# Fix permissions if needed
chmod 644 input.hdf
chmod 755 output_directory
```

### "KeyError: 'some_key'"

**Problem**: HDF5 file is missing expected data fields.

**Solution**:
- Verify file is a valid XPCS analysis output
- Check file was created by compatible XPCS analysis software
- Examine file structure: `h5ls -r file.hdf`

### "OSError: Unable to open file"

**Problem**: HDF5 file is corrupted or in use.

**Solution**:
- Verify file integrity
- Ensure file is not being written to
- Try copying file and processing the copy

### "Address already in use"

**Problem**: Port is already in use by another application.

**Solution**:
```bash
# Use different port
xpcs_webplot serve ./html --port 8080

# Or find and stop process using the port
lsof -i :5000
kill <PID>
```

## Web Server Issues

### I can't access the web server from another computer

**Problem**: Server is bound to localhost only.

**Solution**:
```bash
# Bind to all interfaces
xpcs_webplot serve ./html --host 0.0.0.0

# Then access from other computer using server's IP
# http://<server-ip>:5000
```

**Security Note**: Only do this on trusted networks!

### The web page shows "404 Not Found"

**Problem**: Results directory is empty or path is wrong.

**Solution**:
- Verify HTML folder contains result folders
- Check path is correct: `ls -l ./html`
- Ensure you've run conversion first

### Images don't load on the web page

**Problem**: Image paths are incorrect or files are missing.

**Solution**:
- Check that image files exist in result folder
- Verify file permissions: `ls -l html/result_folder/`
- Try regenerating with `--overwrite`

### The combined summary page is empty

**Problem**: No valid result folders found.

**Solution**:
- Ensure result folders contain `summary.html` files
- Check folder structure is correct
- Run combine command again:
  ```bash
  xpcs_webplot combine ./html
  ```

## Data and Output

### Where is the output saved?

By default, output is saved to `./html/<filename>/` where `<filename>` is the input file name without extension.

### What files are created?

For each input file, the following are created:

- `summary.html` - Main summary page
- `metadata.json` - Extracted metadata
- `*.png` - Plot images (SAXS, stability, correlation, twotime)
- `*.txt` - Exported data files (if not using `--image-only`)

### Can I change the output structure?

The basic structure is fixed, but you can:
- Change output directory with `--target-dir`
- Skip image subdirectory with `--no-create-image-directory`
- Skip data files with `--no-save-result`

### How do I export data in different formats?

Currently, data is exported as tab-separated text files. For other formats:

1. Read the text files with your preferred tool
2. Convert using Python/pandas:
   ```python
   import pandas as pd
   df = pd.read_csv('c2_g2.txt', sep='\t')
   df.to_csv('output.csv')
   df.to_excel('output.xlsx')
   ```

### Can I customize the HTML templates?

Yes! Templates are in `src/xpcs_webplot/templates/`. You can:

1. Modify existing templates
2. Create custom templates
3. Use Jinja2 template inheritance

See [Development Guide](development_guide.md) for details.

### How do I delete old results?

```bash
# Delete specific result folder
rm -rf html/old_result/

# Delete all results
rm -rf html/*/

# Keep only recent results (older than 30 days)
find html/ -type d -mtime +30 -exec rm -rf {} +
```

## Advanced Questions

### Can I use this programmatically in my Python code?

Yes! See [API Reference](api_reference.md) for details:

```python
from xpcs_webplot.converter import convert_xpcs_result

convert_xpcs_result('data.hdf', target_dir='output')
```

### Can I run this on a cluster?

Yes! You can:

1. Submit batch jobs for parallel processing
2. Use the monitoring mode on a head node
3. Deploy the web server for result viewing

### How do I integrate this into my analysis pipeline?

```python
# Example pipeline
from xpcs_webplot.converter import convert_xpcs_result

def my_pipeline(raw_data):
    # Your analysis code
    analyzed_file = run_xpcs_analysis(raw_data)
    
    # Convert to web format
    convert_xpcs_result(analyzed_file, target_dir='results')
    
    return analyzed_file
```

### Can I add custom plots?

Yes! See [Development Guide](development_guide.md) for instructions on:

1. Adding plot functions to `plot_images.py`
2. Calling them from `converter.py`
3. Updating HTML templates

### How do I contribute to the project?

See [Development Guide](development_guide.md) for:

- Setting up development environment
- Code style guidelines
- Testing requirements
- Pull request process

## Still Need Help?

If your question isn't answered here:

1. **Check the documentation**:
   - [User Guide](user_guide.md)
   - [API Reference](api_reference.md)
   - [Architecture](architecture.md)

2. **Search GitHub Issues**:
   - [Existing issues](https://github.com/AZjk/xpcs_webplot/issues)
   - Someone may have had the same problem

3. **Create a new issue**:
   - Provide detailed description
   - Include error messages
   - Share minimal example to reproduce

4. **Contact maintainers**:
   - See README for contact information

## Common Workflows

### Quick Preview Workflow

```bash
# Fast conversion for quick preview
xpcs_webplot plot data.hdf --dpi 120 --num-img 2 --image-only

# View results
xpcs_webplot serve ./html
```

### Publication Quality Workflow

```bash
# High-quality output
xpcs_webplot plot data.hdf --dpi 600 --num-img 12

# Results ready for publication
```

### Batch Processing Workflow

```bash
# Process all files in parallel
xpcs_webplot plot /data/experiment/*.hdf --num-processes 8

# Combine results
xpcs_webplot combine ./html

# Serve for review
xpcs_webplot serve ./html
```

### Continuous Monitoring Workflow

```bash
# Terminal 1: Monitor and process
xpcs_webplot plot /data/incoming --monitor --target-dir ./results

# Terminal 2: Serve results
xpcs_webplot serve ./results

# Results automatically appear as files are processed
```
