import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path

logger = logging.getLogger(__name__)

# Global app instance will be configured later
app = None

# Default configuration
DEFAULT_HTML_FOLDER = 'html'
DEFAULT_RESULTS_SUBFOLDER = 'results'


def get_subdirectories(html_folder):
    """Get list of subdirectories that contain result folders.
    
    This function distinguishes between:
    - Result folders (directories with summary.html directly inside)
    - Subdirectories (directories containing result folders)
    """
    subdirs = []
    
    if not os.path.exists(html_folder):
        return subdirs
    
    for item in os.listdir(html_folder):
        item_path = os.path.join(html_folder, item)
        
        # Skip if not a directory
        if not os.path.isdir(item_path):
            continue
        
        # Skip if this is itself a result folder (has summary.html directly)
        if os.path.exists(os.path.join(item_path, "summary.html")):
            continue
        
        # Skip the special results subfolder
        if item == DEFAULT_RESULTS_SUBFOLDER:
            continue
        
        # Check if this subdirectory contains any result folders
        has_results = False
        for subitem in os.listdir(item_path):
            subitem_path = os.path.join(item_path, subitem)
            if os.path.isdir(subitem_path):
                summary_html = os.path.join(subitem_path, "summary.html")
                if os.path.exists(summary_html):
                    has_results = True
                    break
        
        if has_results:
            # Count the number of result folders
            result_count = 0
            for subitem in os.listdir(item_path):
                subitem_path = os.path.join(item_path, subitem)
                if os.path.isdir(subitem_path):
                    summary_html = os.path.join(subitem_path, "summary.html")
                    if os.path.exists(summary_html):
                        result_count += 1
            
            subdirs.append({
                'name': item,
                'path': item,
                'result_count': result_count
            })
    
    subdirs.sort(key=lambda x: x['name'])
    return subdirs


def get_html_data(html_folder, subdir=None):
    """Extract metadata from all HTML folders.
    
    Args:
        html_folder: Base HTML folder path
        subdir: Optional subdirectory to scan within html_folder
    
    Returns:
        Dictionary with 'type', 'subdirs', and 'results' keys
    """
    # Determine the actual folder to scan
    scan_folder = os.path.join(html_folder, subdir) if subdir else html_folder
    
    html_info = []
    
    if not os.path.exists(scan_folder):
        return {'type': 'flat', 'subdirs': [], 'results': html_info}
    
    # If no subdir specified, check if we have subdirectories with results
    if not subdir:
        subdirs = get_subdirectories(html_folder)
        if subdirs:
            return {'type': 'subdirs', 'subdirs': subdirs, 'results': []}
    
    # Get all directories in the scan folder
    for item in os.listdir(scan_folder):
        item_path = os.path.join(scan_folder, item)
        
        # Skip if not a directory or if it's the results subfolder
        if not os.path.isdir(item_path) or item == DEFAULT_RESULTS_SUBFOLDER:
            continue
        
        # Check if summary.html exists in this directory
        summary_html = os.path.join(item_path, "summary.html")
        if not os.path.exists(summary_html):
            continue
            
        # Look for metadata.json in the metadata subdirectory (new structure)
        json_fname = os.path.join(item_path, "metadata", "metadata.json")
        
        # Fallback to old structure (metadata.json in root)
        if not os.path.exists(json_fname):
            json_fname = os.path.join(item_path, "metadata.json")
        
        # Construct the folder path relative to html_folder
        if subdir:
            folder_path = f"{subdir}/{item}"
        else:
            folder_path = item
        
        if os.path.exists(json_fname):
            try:
                with open(json_fname, "r") as f:
                    meta = json.load(f)
                    
                # Extract required fields
                analysis_type = meta.get("analysis_type", "Unknown")
                start_time = meta.get("start_time", "")
                plot_time = meta.get("plot_time", "")
                
                # Create entry with summary.html path
                html_info.append({
                    'name': item.rstrip("_results"),
                    'folder': folder_path,
                    'summary_html': f"{folder_path}/summary.html",
                    'analysis_type': analysis_type,
                    'start_time': start_time,
                    'plot_time': plot_time,
                    'metadata': meta
                })
            except Exception as e:
                logger.error(f"Error reading metadata for {item}: {str(e)}")
        else:
            # If no metadata found, still include the folder with summary.html
            html_info.append({
                'name': item.rstrip("_results"),
                'folder': folder_path,
                'summary_html': f"{folder_path}/summary.html",
                'analysis_type': "Unknown",
                'start_time': "",
                'plot_time': "",
                'metadata': {}
            })
    
    # Sort by start_time (newest first)
    html_info.sort(key=lambda x: x['start_time'], reverse=True)
    
    return {'type': 'flat', 'subdirs': [], 'results': html_info}


def create_app(html_folder=DEFAULT_HTML_FOLDER):
    """Factory function to create Flask app with custom HTML folder."""
    flask_app = Flask(__name__, template_folder='templates')
    
    # Configuration
    flask_app.config['HTML_FOLDER'] = html_folder
    flask_app.config['RESULTS_SUBFOLDER'] = DEFAULT_RESULTS_SUBFOLDER
    
    @flask_app.route('/')
    def index():
        """Main index page with dynamic content."""
        html_data = get_html_data(flask_app.config['HTML_FOLDER'])
        return render_template('flask_index.html', 
                             data_type=html_data['type'],
                             subdirs=html_data['subdirs'],
                             results=html_data['results'])

    @flask_app.route('/api/data')
    def api_data():
        """API endpoint for getting data with filtering."""
        html_data = get_html_data(flask_app.config['HTML_FOLDER'])
        results = html_data['results']
        
        # Apply filters if provided
        filename_filter = request.args.get('filename', '').lower()
        analysis_filter = request.args.get('analysis_type', '').lower()
        
        if filename_filter or analysis_filter:
            filtered_data = []
            for item in results:
                if filename_filter and filename_filter not in item['name'].lower():
                    continue
                if analysis_filter and analysis_filter not in item['analysis_type'].lower():
                    continue
                filtered_data.append(item)
            results = filtered_data
        
        return jsonify(results)

    @flask_app.route('/subdir/<subdir_name>')
    def view_subdir(subdir_name):
        """View combined summary page for a subdirectory."""
        html_data = get_html_data(flask_app.config['HTML_FOLDER'], subdir=subdir_name)
        results = html_data['results']
        
        if not results:
            return f"No results found in subdirectory: {subdir_name}", 404
        
        return render_template('flask_subdir.html', 
                             subdir_name=subdir_name,
                             results=results)


    @flask_app.route('/view/<folder_name>')
    def view_result(folder_name):
        """View individual result page."""
        folder_path = os.path.join(flask_app.config['HTML_FOLDER'], folder_name)
        
        if not os.path.exists(folder_path):
            return "Result not found", 404
        
        # Read metadata
        json_fname = os.path.join(folder_path, "metadata.json")
        if not os.path.exists(json_fname):
            return "Metadata not found", 404
        
        with open(json_fname, "r") as f:
            metadata = json.load(f)
        
        # Prepare data for template
        data_dict = {
            'title': folder_name.rstrip("_results"),
            'folder': folder_name,
            'metadata': metadata,
            'scattering': f"{folder_name}/saxs_mask.png",
            'stability': f"{folder_name}/stability.png",
        }
        
        # Get correlation images
        files = os.listdir(folder_path)
        png_files = [f for f in files if f.endswith('.png')]
        
        # Remove scattering and stability from list
        if 'saxs_mask.png' in png_files:
            png_files.remove('saxs_mask.png')
        if 'stability.png' in png_files:
            png_files.remove('stability.png')
        
        # Sort correlation images
        png_files.sort()
        
        # Separate g2 and c2 correlation images
        correlation_g2 = []
        correlation_c2 = []
        
        for f in png_files:
            if 'g2' in f.lower():
                correlation_g2.append(f"{folder_name}/{f}")
            elif 'c2' in f.lower():
                correlation_c2.append(f"{folder_name}/{f}")
            else:
                # Default to g2 if not specified
                correlation_g2.append(f"{folder_name}/{f}")
        
        data_dict['correlation_g2'] = correlation_g2
        data_dict['correlation_c2'] = correlation_c2
        
        return render_template('flask_single.html', mydata=data_dict)

    @flask_app.route('/results/<path:folder_name>/summary.html')
    def serve_summary(folder_name):
        """Serve summary.html from a specific results folder."""
        # Get absolute path to HTML folder
        html_folder_abs = os.path.abspath(flask_app.config['HTML_FOLDER'])
        folder_path = os.path.join(html_folder_abs, folder_name)
        summary_path = os.path.join(folder_path, 'summary.html')
        
        logger.info(f"Attempting to serve summary from: {summary_path}")
        logger.info(f"File exists: {os.path.exists(summary_path)}")
        logger.info(f"HTML_FOLDER (abs): {html_folder_abs}")
        logger.info(f"folder_name: {folder_name}")
        
        if not os.path.exists(summary_path):
            return f"Summary not found at: {summary_path}", 404
        
        # Use send_file with absolute path
        from flask import send_file
        return send_file(summary_path)

    @flask_app.route('/results/<path:folder_name>/<path:filepath>')
    def serve_result_files(folder_name, filepath):
        """Serve static files (images, etc.) from within a specific results folder."""
        # Get absolute path to the result folder
        html_folder_abs = os.path.abspath(flask_app.config['HTML_FOLDER'])
        folder_path = os.path.join(html_folder_abs, folder_name)
        
        # Security check: ensure the folder exists and is a directory
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return "Folder not found", 404
        
        # Serve the file from the result folder
        return send_from_directory(folder_path, filepath)

    @flask_app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files from the HTML folder."""
        return send_from_directory(flask_app.config['HTML_FOLDER'], filename)
    
    return flask_app


def main():
    """Main entry point for the Flask server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run XPCS WebPlot Flask server')
    parser.add_argument('--html-folder', default=DEFAULT_HTML_FOLDER, 
                        help='Path to the HTML folder containing results (default: html)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to run the server on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Create app with proper configuration
    flask_app = create_app(args.html_folder)
    
    print(f"Starting XPCS WebPlot server...")
    print(f"HTML folder: {args.html_folder}")
    print(f"Server running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    flask_app.run(debug=args.debug, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
