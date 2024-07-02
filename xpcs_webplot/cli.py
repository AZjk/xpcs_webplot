"""
single hdf plot tool for globus
"""
from .plot_images import hdf2web_safe as hdf2web
import argparse
import logging
import sys
from .webplot_cli import local_plot


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s | %(message)s',
                    datefmt='%m-%d %H:%M:%S')

def globus_plot():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('fname', metavar='FNAME', type=str,
                        help='the hdf filename')

    parser.add_argument('--target_dir', type=str, nargs='?', default='/tmp',
                        help='output directory')

    parser.add_argument('--num_img', type=int, nargs='?', default=4,
                        help='number of images per row')

    parser.add_argument('--dpi', type=int, nargs='?', default=240,
                        help=('dpi controls the image resolution.'
                              'For 4K monitors, dpi can be set to 240 to '
                              'produce images with 3840 horizontal pixels.'))

    parser.add_argument('--overwrite', type=bool, nargs='?',
                        default=True, help='overwrite flag')

    # parser.add_argument('--backend', type=str, default='matplotlib',
    #                     help='backend to use for the plotting.')

    kargs = vars(parser.parse_args())
    fname = kargs.pop('fname')
    # hdf2web(fname, image_only=True, **kargs)
    hdf2web(fname, image_only=False, **kargs)


def main():
    # local method for 8IDI, it will compile the image to html
    # it reads the setting from .xpcs_webplot/default_setting.json
    if len(sys.argv[0]) > 1 and sys.argv[1] == '__local__':
        return local_plot()
    # for globus plot. only plot images;
    else:
        return globus_plot()


if __name__ == '__main__':
    sys.exit(main())