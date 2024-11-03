import glob
import os
from .plot_images import hdf2web_safe as hdf2web
from .plot_images import hdf2web_safe_fixed as hdf2web_fixed
from .html_utlits import combine_all_htmls
import json
import sys
import datetime
import logging

logger = logging.getLogger(__name__)


def convert_many_files(flist, num_workers=24, **kwargs):
    assert isinstance(flist, list)

    tot_num = len(flist)

    # wrap the args and kwargs in two list to pass to starmap
    args = [(x,) for x in flist]
    kwargs = [kwargs.copy() for _ in range(tot_num)]
    full_input = zip(args, kwargs)

    from multiprocessing import Pool
    p = Pool(min(num_workers, tot_num))
    p.starmap(hdf2web_fixed, full_input)


def convert_folder(folder, **kwargs):
    if os.path.isdir(folder):
        folder = folder.rstrip('/')
        flist = glob.glob(folder + '/*.hdf')
        flist.sort()
        convert_many_files(flist, **kwargs)


def convert_one_file(fname=None, **kwargs):
    return hdf2web(fname, **kwargs)


def generate_random_dir(prefix='/net/wolf/data/xpcs8/2022-1/html'):
# def generate_random_dir(prefix='/local/data_miaoqi/html'):
    import uuid
    new_id = str(uuid.uuid4())[-12:]
    new_dir = os.path.join(prefix, new_id)
    logger.info(f"New random directory is {new_dir}")
    if os.mkdir(new_dir):
        logger.info(f"New directory {new_dir} is created.")


if __name__ == '__main__':
    local_plot()
