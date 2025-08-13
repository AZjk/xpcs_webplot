# Flask Migration Guide for XPCS WebPlot

This guide explains how to migrate from the static HTML generation approach to the new Flask-based dynamic web server.

## Overview

The project has been updated to use Flask for dynamic content serving instead of generating static HTML files. This provides several benefits:

- **Dynamic content**: No need to regenerate HTML files when data changes
- **Search and filtering**: Real-time search and filter functionality
- **Better performance**: Only loads data when needed
- **Improved UI**: Modern, responsive interface with better navigation

## New Features

### 1. Dynamic Index Page
- Real-time search by filename and analysis type
- Sortable columns (click headers to sort)
- Shows result count with filtering
- Clean, modern UI design

### 2. Enhanced Result Viewing
- Sticky navigation bar
- Smooth scrolling between sections
- Grid layout for correlation images
- Back to dashboard button
- Responsive design

### 3. Flask Server
- Command-line interface with options
- Configurable host, port, and HTML folder
- Debug mode support
- API endpoint for data access

## Installation

1. Install the updated dependencies:
```bash
pip install -r requirements.txt
```

Or if using pyproject.toml:
```bash
pip install -e .
```

## Migration Steps

### Option 1: Keep existing structure
If you want to keep your existing HTML folder structure:

```bash
# Simply run the Flask server
xpcs_webplot_server --html-folder html
```

### Option 2: Organize with subfolder
To organize result folders into a subfolder:

```bash
# Run the migration script
python -m xpcs_webplot.migrate_to_flask --html-folder html --create-subfolder

# Then run the server pointing to the results subfolder
xpcs_webplot_server --html-folder html/results
```

## Running the Flask Server

### Basic usage:
```bash
xpcs_webplot_server
```

### With options:
```bash
xpcs_webplot_server --html-folder /path/to/html --host 0.0.0.0 --port 5000 --debug
```

### Available options:
- `--html-folder`: Path to the HTML folder containing results (default: html)
- `--host`: Host to run the server on (default: 0.0.0.0)
- `--port`: Port to run the server on (default: 5000)
- `--debug`: Run in debug mode

## API Endpoints

The Flask server provides the following endpoints:

- `/`: Main dashboard page
- `/view/<folder_name>`: View individual result
- `/api/data`: JSON API for data with optional filtering
  - Query parameters: `filename`, `analysis_type`
- `/static/<path>`: Serve static files (images, etc.)

## Updating Your Workflow

### Before (static approach):
```python
from xpcs_webplot.html_utlits import combine_all_htmls
combine_all_htmls("html")
# Open static index.html in browser
```

### After (Flask approach):
```bash
# Start the server
xpcs_webplot_server --html-folder html

# Open http://localhost:5000 in browser
```

## Troubleshooting

### Port already in use
If port 5000 is already in use, specify a different port:
```bash
xpcs_webplot_server --port 8080
```

### Can't access from other machines
Make sure to use host 0.0.0.0 (default) instead of localhost:
```bash
xpcs_webplot_server --host 0.0.0.0
```

### Missing dependencies
Make sure Flask is installed:
```bash
pip install flask
```

## Benefits of Flask Approach

1. **No HTML regeneration**: Changes to data are immediately visible
2. **Better performance**: Only loads data when needed
3. **Search functionality**: Filter results without page reload
4. **Sorting**: Click column headers to sort
5. **Modern UI**: Cleaner, more responsive interface
6. **API access**: JSON API for programmatic access
7. **Extensible**: Easy to add new features

## Future Enhancements

The Flask-based approach opens up possibilities for:
- User authentication
- Database integration
- Advanced filtering and search
- Data export functionality
- Real-time updates
- RESTful API expansion
