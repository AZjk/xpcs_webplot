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
    parser = argparse.ArgumentParser(description="Process some integers.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    plot_command = subparsers.add_parser("plot", help="plot images from hdf result files")
    plot_command.add_argument("fname", type=str,
                        help="the hdf filename or the folder that the results are stored")

    plot_command.add_argument("--target-dir", type=str, nargs="?", default="/tmp",
                        help="output directory")

    plot_command.add_argument("--image-only", action="store_true",
                              help="only generate images, no html")

    plot_command.add_argument("--num-img", type=int, nargs="?", default=4,
                        help="number of images per row")

    plot_command.add_argument("--dpi", type=int, nargs="?", default=240,
                        help=("dpi controls the image resolution."
                              "For 4K monitors, dpi can be set to 240 to "
                              "produce images with 3840 horizontal pixels."))

    plot_command.add_argument("--overwrite", action="store_true",
                              help="overwrite flag")

    plot_command.add_argument("--monitor", action="store_true",
                              help="whether to monitor the folder for new files")

    plot_command.add_argument("--num-workers", type=int, default=8,
                              help="number of parallel worker processes for file conversion")
    plot_command.add_argument("--max-running-time", type=int, default=86400 * 7,
                              help="maximum running time in seconds")
    
    combine_command = subparsers.add_parser("combine", help="combine htmls in one")
    combine_command.add_argument("target_dir", type=str, nargs="?",
                                help="the plot directory to combine")
    
    serve_command = subparsers.add_parser("serve", help="serve the htmls with Flask web server")
    serve_command.add_argument("target_dir", type=str, nargs="?", default=".",
                               help="the HTML folder containing XPCS results")
    serve_command.add_argument("--port", type=int, help="port to run the Flask server",
                              default=5000)
    serve_command.add_argument("--host", type=str, default="0.0.0.0",
                               help="host to run the Flask server on (default: 0.0.0.0)")
    
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
        combine_all_htmls(kwargs["target_dir"])
    elif command == "serve":
        run_flask_server(kwargs["target_dir"], kwargs["port"], kwargs["host"])
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())
