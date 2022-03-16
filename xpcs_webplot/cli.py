from .plot_images import hdf2web_safe as hdf2web
import argparse


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('fname', metavar='FNAME', type=str,
                        help='the hdf filename')

    parser.add_argument('--target_dir', type=str, nargs='?', default='/tmp',
                        help='output directory')

    parser.add_argument('--num_img', type=int, nargs='?', default=4,
                        help='number of images per row')

    parser.add_argument('--dpi', type=int, nargs='?', default=240,
                        help=('dpi controls the image resolution.'
                              'For 4K/3840px, dpi is 240'))

    parser.add_argument('--overwrite', type=bool, nargs='?',
                        default=True, help='overwrite flag')

    kargs = vars(parser.parse_args())
    fname = kargs.pop('fname')
    hdf2web(fname, image_only=True, **kargs)


if __name__ == '__main__':
    main()