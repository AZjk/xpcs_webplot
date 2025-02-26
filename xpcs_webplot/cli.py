import argparse
import logging
import sys
import os
import glob
from .webplot_cli import combine_all_htmls, convert_one_file, convert_many_files 
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import time
from functools import partial

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s | %(message)s',
                    datefmt='%m-%d %H:%M:%S')
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
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, handler)
    local_ip = get_local_ip()
    print(f"Serving directory: {target_dir}")
    print(f"Server running at:")
    print(f" - Local:   http://localhost:{port}")
    print(f" - Network: http://{local_ip}:{port}")
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    plot_command = subparsers.add_parser('plot', help='plot images from hdf result files')
    plot_command.add_argument('fname', type=str,
                        help='the hdf filename or the folder that the results are stored')

    plot_command.add_argument('--target_dir', type=str, nargs='?', default='/tmp',
                        help='output directory')

    plot_command.add_argument('--image_only', action='store_true',
                              help='only generate images, no html')

    plot_command.add_argument('--num_img', type=int, nargs='?', default=4,
                        help='number of images per row')

    plot_command.add_argument('--dpi', type=int, nargs='?', default=240,
                        help=('dpi controls the image resolution.'
                              'For 4K monitors, dpi can be set to 240 to '
                              'produce images with 3840 horizontal pixels.'))

    plot_command.add_argument('--overwrite', action='store_true',
                              help='overwrite flag')

    plot_command.add_argument('--combinetime', type=str, choices=['never', 'end', 'each'],
                              default='each',
                              help='choose when to combine the newly plotted html with the index html')

    plot_command.add_argument('--monitor_interval_seconds', type=int, default=30,
                             help="""if plotting a folder, you can choose to
                             keep monitoring the folder every monito_interval_seconds 
                             for the new files and plotting them. """)
    
    combine_command = subparsers.add_parser('combine', help='combine htmls in one')
    combine_command.add_argument('target_dir', type=str, nargs='?',
                                help='the plot directory to combine')
    
    serve_command = subparsers.add_parser('serve', help='serve the htmls')
    serve_command.add_argument('--target_dir', type=str, default='.',
                               help='the plot directory to host the server')
    serve_command.add_argument('--port', type=int, help='port to run the http server',
                              default=8081)
    
    args = parser.parse_args()
    kwargs = vars(parser.parse_args())
    logger.info('|'.join([f'{k}:{v}' for k, v in kwargs.items()]))
    command = kwargs.pop('command', None)

    max_running_time = 3600 * 24 * 7    # 7 days
    if command == 'plot':
        fname = kwargs.pop('fname')
        combinetime = kwargs.pop('combinetime')
        monito_interval_seconds = kwargs.pop('monitor_interval_seconds')
        if os.path.isfile(fname):
            convert_one_file(fname, **kwargs)
            if combinetime in ['end', 'each']:
                combine_all_htmls(kwargs['target_dir'])
        # a directory rather than a single file
        else:
            t0 = time.time()
            while True:
                flist = glob.glob(os.path.join(fname, '*.hdf'))
                flist.sort(key=os.path.getctime)
                convert_many_files(flist, num_workers=8, **kwargs)
                combine_all_htmls(kwargs['target_dir'])

                # if combinetime == 'each':
                #     for f in flist:
                #         if convert_one_file(f, **kwargs):
                #             combine_all_htmls(kwargs['target_dir'])
                # else:
                #     # it is 'never' or 'end'
                #     flag = False
                #     for f in flist:
                #         flag = flag or convert_one_file(f, **kwargs)
                #     if flag:
                #         combine_all_htmls(kwargs['target_dir'])
                logger.info(f'check new files in {monito_interval_seconds} seconds')
                time.sleep(monito_interval_seconds)
                t1 = time.time()
                if t1 - t0 > max_running_time:
                    logger.info(f'max running time {max_running_time} seconds reached, exit')
                    break

    elif command == 'combine':
        combine_all_htmls(kwargs['target_dir'])
    elif command == 'serve':
        run_server(kwargs['target_dir'], kwargs['port'])
    else:
        parser.print_help()


if __name__ == '__main__':
    sys.exit(main())
