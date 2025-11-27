import glob
import os
from .converter import convert_xpcs_result_safe, convert_xpcs_result_wrap
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
    p.starmap(convert_xpcs_result_wrap, full_input)


def convert_folder(folder, **kwargs):
    if os.path.isdir(folder):
        folder = folder.rstrip("/")
        flist = glob.glob(folder + "/*.hdf")
        flist.sort()
        convert_many_files(flist, **kwargs)


def convert_one_file(fname=None, **kwargs):
    return convert_xpcs_result_safe(fname, **kwargs)



if __name__ == "__main__":
    pass
