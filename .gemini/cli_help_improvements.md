# CLI Help Message Improvements

## Summary

Enhanced the command-line interface help messages for `xpcs-webplot` to be significantly more informative and user-friendly. The improvements provide clear descriptions of what the tool does, detailed explanations of each option, and practical examples.

## Changes Made

### Main Command Help (`xpcs-webplot --help`)

**Before:**
- Generic description: "Process some integers."
- Minimal subcommand listing

**After:**
- Comprehensive description explaining the tool's purpose: converting XPCS HDF5 files to interactive web visualizations
- Clear explanation of all three subcommands (plot, combine, serve)
- Practical examples showing common usage patterns
- Better formatting with `RawDescriptionHelpFormatter`

### Plot Subcommand (`xpcs-webplot plot --help`)

**Improvements:**
- **Description**: Explains that it converts XPCS HDF5 files to interactive HTML with plots, and can process single files, directories, or monitor continuously
- **Enhanced argument help**:
  - `fname`: Now clearly states "Path to HDF5 file or directory containing HDF files to process"
  - `--target-dir`: Specifies it's for "Output directory for generated HTML and image files (default: /tmp)"
  - `--image-only`: Clarifies "Generate only plot images without HTML summary pages"
  - `--num-img`: Explains "Number of plot images to display per row in HTML output (default: 4)"
  - `--dpi`: Detailed explanation with practical guidance for different monitor types
  - `--monitor`: Comprehensive explanation of monitoring mode with usage notes
  - `--num-workers`: Clear description of parallel processing (default: 8)
  - `--max-running-time`: Explains auto-stopping behavior (default: 7 days)
- **Examples section**: Four practical examples covering different use cases

### Combine Subcommand (`xpcs-webplot combine --help`)

**Improvements:**
- **Description**: Explains it generates a combined index page aggregating all HTML results
- **Enhanced argument help**:
  - `target_dir`: "Directory containing HTML files to combine into a single index page"
- **Example**: Shows typical usage

### Serve Subcommand (`xpcs-webplot serve --help`)

**Improvements:**
- **Description**: Explains Flask server functionality and features (subdirectory navigation, combined summaries)
- **Enhanced argument help**:
  - `target_dir`: "Directory containing HTML result files to serve (default: current directory)"
  - `--port`: "Port number for the Flask server (default: 5000)"
  - `--host`: Detailed explanation of network vs. localhost access
- **Examples section**: Shows both local-only and network access configurations
- **Additional guidance**: Instructions on accessing the server and stopping it

## Benefits

1. **Self-documenting**: Users can understand the tool's capabilities without external documentation
2. **Clear defaults**: All default values are explicitly stated
3. **Practical guidance**: Examples show real-world usage patterns
4. **Better UX**: Users can quickly find the right command and options for their needs
5. **Professional**: Help messages now match the quality of the well-documented codebase

## Testing

All help messages have been tested and display correctly:
- ✅ Main help: `xpcs-webplot --help`
- ✅ Plot help: `xpcs-webplot plot --help`
- ✅ Combine help: `xpcs-webplot combine --help`
- ✅ Serve help: `xpcs-webplot serve --help`
