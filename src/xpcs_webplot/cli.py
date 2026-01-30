import argparse
import logging
import sys
import os
import glob
from .webplot_cli import convert_one_file, convert_many_files 
from .html_utlits import combine_all_htmls
from .monitor_and_process import monitor_and_process
from .flask_app import create_app


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s.%(msecs)03d %(name)s %(levelname)s | %(message)s",
                    datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)



def run_flask_server(html_folder=".", port=5000, host="0.0.0.0"):
    """
    Start Flask web server to serve XPCS webplot results.

    Launches a Flask development server that provides a web interface for
    browsing and viewing XPCS analysis results.

    Parameters
    ----------
    html_folder : str, optional
        Path to the folder containing HTML results to serve. Default is "." (current directory).
    port : int, optional
        Port number on which to run the Flask server. Default is 5000.
    host : str, optional
        Host address to bind the server to. Use "0.0.0.0" to make the server
        accessible from other machines on the network, or "127.0.0.1" for
        localhost only. Default is "0.0.0.0".

    Returns
    -------
    None

    Notes
    -----
    The server runs in non-debug mode for production use. Press Ctrl+C to stop
    the server.

    See Also
    --------
    create_app : Flask application factory

    Examples
    --------
    >>> run_flask_server('html', port=8080, host='127.0.0.1')
    Starting XPCS WebPlot Flask server...
    """
    app = create_app(html_folder)
    
    print(f"Starting XPCS WebPlot Flask server...")
    print(f"HTML folder: {html_folder}")
    print(f"Server running at:")
    print(f" - Local:   http://localhost:{port}")
    print(f" - Network: http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=False, host=host, port=port)


def main():
    """
    Main entry point for the XPCS webplot command-line interface.

    Provides a command-line interface with three subcommands:
    - plot: Convert XPCS HDF files to web-viewable format
    - combine: Combine multiple HTML results into a single index
    - serve: Start Flask web server to view results

    Returns
    -------
    None or int
        Returns None on success, or exits with error code on failure.

    Notes
    -----
    The CLI supports the following commands:
    
    plot command:
        Convert HDF files to web format with plots and HTML summaries.
        Can process single files, directories, or monitor directories for new files.
        
    combine command:
        Generate a combined index page for multiple HTML results.
        
    serve command:
        Launch Flask web server to browse and view results interactively.

    Examples
    --------
    Convert a single file:
    $ xpcs-webplot plot data.hdf --target-dir output --dpi 300
    
    Convert all files in a directory:
    $ xpcs-webplot plot /path/to/data --target-dir output --num-workers 8
    
    Monitor a directory for new files:
    $ xpcs-webplot plot /path/to/data --monitor --target-dir output
    
    Serve results with Flask:
    $ xpcs-webplot serve output --port 8080

    See Also
    --------
    convert_one_file : Convert a single HDF file
    convert_many_files : Convert multiple HDF files
    monitor_and_process : Monitor directory for new files
    run_flask_server : Start Flask web server
    """
    parser = argparse.ArgumentParser(
        prog="xpcs-webplot",
        description=(
            "XPCS WebPlot - Convert XPCS HDF5 result files to interactive web visualizations. "
            "Generate HTML pages with plots from X-ray Photon Correlation Spectroscopy data, "
            "monitor directories for new files, combine results, and serve them via Flask web server."
        ),
        epilog=(
            "Examples:\n"
            "  xpcs-webplot plot data.hdf --target-dir output\n"
            "  xpcs-webplot plot /data/dir --monitor --num-workers 8\n"
            "  xpcs-webplot combine output\n"
            "  xpcs-webplot serve output --port 8080\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Choose one of the following commands:",
        help="Command to execute"
    )

    plot_command = subparsers.add_parser(
        "plot",
        help="Convert XPCS HDF5 files to web-viewable HTML with plots",
        description=(
            "Convert XPCS HDF5 result files into interactive HTML pages with plots. "
            "Can process a single file, all HDF files in a directory, or continuously "
            "monitor a directory for new files and process them automatically."
        ),
        epilog=(
            "Examples:\n"
            "  Single file:    xpcs-webplot plot data.hdf --target-dir output\n"
            "  Directory:      xpcs-webplot plot /data/dir --target-dir output --num-workers 8\n"
            "  Monitor mode:   xpcs-webplot plot /data/dir --monitor --target-dir output\n"
            "  High-res plots: xpcs-webplot plot data.hdf --dpi 300 --num-img 6\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    plot_command.add_argument(
        "fname",
        type=str,
        help="Path to HDF5 file or directory containing HDF files to process"
    )

    plot_command.add_argument(
        "--html-dir",
        type=str,
        nargs="?",
        default="/tmp",
        help="Output directory for generated HTML and image files (default: /tmp)"
    )

    plot_command.add_argument(
        "--image-only",
        action="store_true",
        help="Generate only plot images without HTML summary pages"
    )

    plot_command.add_argument(
        "--num-img",
        type=int,
        nargs="?",
        default=4,
        help="Number of plot images to display per row in HTML output (default: 4)"
    )

    plot_command.add_argument(
        "--dpi",
        type=int,
        nargs="?",
        default=240,
        help=(
            "Image resolution in dots per inch. Higher values produce sharper images. "
            "For 4K monitors, use 240 for 3840px width. For HD, use 120-150. (default: 240)"
        )
    )

    plot_command.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files if they already exist"
    )

    plot_command.add_argument(
        "--monitor",
        action="store_true",
        help=(
            "Monitor the directory continuously for new HDF files and process them automatically. "
            "Only works when fname is a directory. Press Ctrl+C to stop monitoring."
        )
    )

    plot_command.add_argument(
        "--num-workers",
        type=int,
        default=8,
        help="Number of parallel worker processes for batch file conversion (default: 8)"
    )
    plot_command.add_argument(
        "--max-running-time",
        type=int,
        default=86400 * 7,
        help="Maximum time in seconds to run in monitor mode before auto-stopping (default: 604800 = 7 days)"
    )
    plot_command.add_argument(
        "--save-result",
        action="store_true",
        default=True,
        help="Save XPCS result data files (SAXS, g2, twotime) to disk (default: True)"
    )
    plot_command.add_argument(
        "--no-save-result",
        dest="save_result",
        action="store_false",
        help="Skip saving XPCS result data files, only generate plots and HTML"
    )
    
    combine_command = subparsers.add_parser(
        "combine",
        help="Combine multiple HTML results into a single index page",
        description=(
            "Generate a combined index page that aggregates all individual HTML result files "
            "in the specified directory. This creates a master summary page for easy navigation "
            "across multiple XPCS analysis results."
        ),
        epilog=(
            "Example:\n"
            "  xpcs-webplot combine /path/to/output\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    combine_command.add_argument(
        "html_dir",
        type=str,
        nargs="?",
        help="Directory containing HTML files to combine into a single index page"
    )
    
    serve_command = subparsers.add_parser(
        "serve",
        help="Start Flask web server to browse and view HTML results interactively",
        description=(
            "Launch a Flask web server that provides an interactive interface for browsing "
            "and viewing XPCS analysis results. The server supports subdirectory navigation "
            "and displays combined summaries for easy data exploration."
        ),
        epilog=(
            "Examples:\n"
            "  Local access only:  xpcs-webplot serve output --host 127.0.0.1 --port 5000\n"
            "  Network access:     xpcs-webplot serve output --host 0.0.0.0 --port 8080\n"
            "\n"
            "After starting, access the server at http://localhost:<port>\n"
            "Press Ctrl+C to stop the server.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    serve_command.add_argument(
        "html_dir",
        type=str,
        nargs="?",
        default=".",
        help="Directory containing HTML result files to serve (default: current directory)"
    )
    serve_command.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number for the Flask server (default: 5000)"
    )
    serve_command.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help=(
            "Host address to bind the server. Use 0.0.0.0 for network access or "
            "127.0.0.1 for localhost only (default: 0.0.0.0)"
        )
    )
    
    kwargs = vars(parser.parse_args())
    logger.info("|".join([f"{k}:{v}" for k, v in kwargs.items()]))

    command = kwargs.pop("command", None)

    if command == "plot":
        fname = kwargs.pop("fname")
        monitor = kwargs.pop("monitor", False)
        # a single file
        if os.path.isfile(fname):
            kwargs.pop("num_workers", None)
            kwargs.pop('max_running_time', None)
            convert_one_file(fname, **kwargs)
        # a directory rather than a single file
        elif os.path.isdir(fname):
            if not monitor:
                flist = glob.glob(os.path.join(fname, "*.hdf"))
                if len(flist) == 0:
                    logger.error(f"No hdf files found in {fname}")
                    return
                kwargs.pop('max_running_time', None)
                convert_many_files(flist, **kwargs)
            else:
                # Validate directory is accessible before starting monitor
                if not os.access(fname, os.R_OK):
                    logger.error(f"Directory is not readable: {fname}")
                    return
                logger.info(f"Monitoring the directory... {fname}")
                monitor_and_process(fname, **kwargs)
        else:
            logger.error(f"Invalid file or directory: {fname}")

    elif command == "combine":
        combine_all_htmls(kwargs["html_dir"])
    elif command == "serve":
        run_flask_server(kwargs["html_dir"], kwargs["port"], kwargs["host"])
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())
