import argparse
import logging
import sys
import os
import glob
from .webplot_cli import convert_one_file, convert_many_files 
from .html_utlits import combine_all_htmls
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from functools import partial
from .monitor_and_process import monitor_and_process


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s.%(msecs)03d %(name)s %(levelname)s | %(message)s",
                    datefmt="%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)



def get_local_ip():
    """
    get local ip address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def run_server(target_dir=".", port=8000):
    """
    run a simple http server to serve the images for target_dir
    """
    # Use partial to create a handler class with the specified directory
    handler = partial(SimpleHTTPRequestHandler, directory=target_dir)
    
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, handler)
    local_ip = get_local_ip()
    print(f"Serving directory: {target_dir}")
    print(f"Server running at:")
    print(f" - Local:   http://localhost:{port}")
    print(f" - Network: http://{local_ip}:{port}")
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    plot_command = subparsers.add_parser("plot", help="plot images from hdf result files")
    plot_command.add_argument("fname", type=str,
                        help="the hdf filename or the folder that the results are stored")

    plot_command.add_argument("--target_dir", type=str, nargs="?", default="/tmp",
                        help="output directory")

    plot_command.add_argument("--image_only", action="store_true",
                              help="only generate images, no html")

    plot_command.add_argument("--num_img", type=int, nargs="?", default=4,
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
                              help="whether to monitor the folder for new files")
    plot_command.add_argument("--max-running-time", type=int, default=86400 * 7,
                              help="maximum running time in seconds")
    
    combine_command = subparsers.add_parser("combine", help="combine htmls in one")
    combine_command.add_argument("target_dir", type=str, nargs="?",
                                help="the plot directory to combine")
    
    serve_command = subparsers.add_parser("serve", help="serve the htmls")
    serve_command.add_argument("--target_dir", type=str, default=".",
                               help="the plot directory to host the server")
    serve_command.add_argument("--port", type=int, help="port to run the http server",
                              default=8081)
    
    kwargs = vars(parser.parse_args())
    logger.info("|".join([f"{k}:{v}" for k, v in kwargs.items()]))

    command = kwargs.pop("command", None)

    if command == "plot":
        fname = kwargs.pop("fname")
        monitor = kwargs.pop("monitor", False)
        # a single file
        if os.path.isfile(fname):
            kwargs.pop("num_workers", None)
            convert_one_file(fname, **kwargs)
            combine_all_htmls(kwargs["target_dir"])
        # a directory rather than a single file
        elif os.path.isdir(fname):
            if not monitor:
                flist = glob.glob(os.path.join(fname, "*.hdf"))
                if len(flist) == 0:
                    logger.error(f"No hdf files found in {fname}")
                    return
                kwargs.pop('max_running_time')
                convert_many_files(flist, **kwargs)
                combine_all_htmls(kwargs["target_dir"])
            else:
                logger.info(f"Monitoring the directory... {fname}")
                monitor_and_process(fname, **kwargs)
        else:
            logger.error(f"Invalid file or directory: {fname}")

    elif command == "combine":
        combine_all_htmls(kwargs["target_dir"])
    elif command == "serve":
        run_server(kwargs["target_dir"], kwargs["port"])
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())
