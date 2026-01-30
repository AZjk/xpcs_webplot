import glob
import os
from .converter import convert_xpcs_result_safe, convert_xpcs_result_wrap
import logging

logger = logging.getLogger(__name__)


def convert_many_files(flist, num_workers=24, **kwargs):
    """
    Convert multiple XPCS HDF files to web format using multiprocessing.

    This function processes a list of HDF files in parallel using a multiprocessing
    pool to generate web-viewable plots and HTML summaries.

    Parameters
    ----------
    flist : list of str
        List of file paths to HDF files to be converted.
    num_workers : int, optional
        Maximum number of worker processes to use for parallel processing.
        The actual number of workers will be the minimum of num_workers and
        the number of files. Default is 24.
    **kwargs : dict
        Additional keyword arguments to pass to the conversion function.
        Common options include:
        - html_dir : str, output directory for generated files
        - num_img : int, number of images per row
        - dpi : int, image resolution
        - overwrite : bool, whether to overwrite existing files
        - image_only : bool, whether to generate only images without HTML

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If flist is not a list.

    See Also
    --------
    convert_one_file : Convert a single HDF file
    convert_folder : Convert all HDF files in a folder

    Examples
    --------
    >>> files = ['file1.hdf', 'file2.hdf', 'file3.hdf']
    >>> convert_many_files(files, num_workers=4, html_dir='output')
    """
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
    """
    Convert all XPCS HDF files in a folder to web format.

    Scans the specified folder for HDF files (*.hdf) and processes them
    using parallel conversion.

    Parameters
    ----------
    folder : str
        Path to the folder containing HDF files to convert.
    **kwargs : dict
        Additional keyword arguments to pass to convert_many_files.
        See convert_many_files for available options.

    Returns
    -------
    None

    Notes
    -----
    - Only processes files with .hdf extension
    - Files are processed in sorted order
    - If folder is not a valid directory, the function returns without error

    See Also
    --------
    convert_many_files : Convert multiple HDF files
    convert_one_file : Convert a single HDF file

    Examples
    --------
    >>> convert_folder('/path/to/data', html_dir='html', num_workers=8)
    """
    if os.path.isdir(folder):
        folder = folder.rstrip("/")
        flist = glob.glob(folder + "/*.hdf")
        flist.sort()
        convert_many_files(flist, **kwargs)


def convert_one_file(fname=None, **kwargs):
    """
    Convert a single XPCS HDF file to web format with error handling.

    This is a wrapper function that calls convert_xpcs_result_safe to process
    a single HDF file and generate web-viewable plots and HTML summaries.

    Parameters
    ----------
    fname : str, optional
        Path to the HDF file to convert. Default is None.
    **kwargs : dict
        Additional keyword arguments to pass to the conversion function.
        Common options include:
        - html_dir : str, output directory for generated files
        - num_img : int, number of images per row
        - dpi : int, image resolution
        - overwrite : bool, whether to overwrite existing files
        - image_only : bool, whether to generate only images without HTML

    Returns
    -------
    bool or None
        True if conversion was successful, False if it failed, or None
        if an exception occurred.

    See Also
    --------
    convert_many_files : Convert multiple HDF files
    convert_folder : Convert all HDF files in a folder
    convert_xpcs_result_safe : The underlying conversion function with error handling

    Examples
    --------
    >>> convert_one_file('data.hdf', html_dir='output', dpi=240)
    True
    """
    return convert_xpcs_result_safe(fname, **kwargs)



if __name__ == "__main__":
    pass
