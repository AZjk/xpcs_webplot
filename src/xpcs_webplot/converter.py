import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
import numpy as np
import skimage.io as skio

from pyxpcsviewer.xpcs_file import XpcsFile as XF

from .html_utlits import convert_to_html
from .metadata_utils import save_metadata, convert_to_native_format
from .plot_images import (
    plot_crop_mask_saxs,
    plot_multitau_correlation,
    plot_stability,
    plot_twotime_correlation,
    rename_files,
)

logger = logging.getLogger(__name__)


def save_xpcs_result(xf_obj: XF, top_dir: Path):
    """
    Save XPCS analysis results to text and image files.

    Exports SAXS data, correlation functions, and twotime analysis results
    from an XPCS file object to a structured directory format for web viewing
    and further analysis.

    Parameters
    ----------
    xf_obj : XpcsFile
        XPCS file object containing analysis results.
    top_dir : Path
        Top-level directory where data will be saved. A 'data' subdirectory
        will be created within this directory.

    Returns
    -------
    None

    Notes
    -----
    The function creates the following files in the data directory:
    - saxs_1d.txt : 1D SAXS profile (q vs Intensity)
    - saxs_1d_stability.txt : Time-resolved 1D SAXS profiles
    - saxs_2d.tif : 2D SAXS pattern
    
    For Multitau analysis:
    - g2.txt : Correlation functions
    - g2_err.txt : Correlation function errors
    - delays.txt : Delay times
    - qbin_values.txt : q-bin values
    
    For Twotime analysis:
    - c2_XXXX.tif : Twotime correlation maps (one per q-bin)
    - c2_g2.txt : g2 from twotime analysis
    - c2_g2_partials.txt : Segmented g2 from twotime analysis

    See Also
    --------
    plot_xpcs_result : Generate plots from XPCS data
    convert_xpcs_result : Main conversion function
    """
    data_dir = top_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Save saxs 1D data
    saxs_1d_path = data_dir / "saxs_1d.txt"
    q, Iq = xf_obj.saxs_1d["q"], xf_obj.saxs_1d["Iq"]
    q = q.reshape(1, -1)
    data = np.vstack((q, Iq)).T
    np.savetxt(saxs_1d_path, data, header="q (1/Å)       Intensity (a.u.)")

    # saxs 1D stability
    saxs_1d_stability_path = data_dir / "saxs_1d_stability.txt"
    q, Iqp = xf_obj.saxs_1d["q"], xf_obj.Iqp
    data = np.stack([q] + [Iqp[n] for n in range(Iqp.shape[0])], axis=0)
    header = " ".join(["q (1/Å)"] + [f"Iq_t{n}" for n in range(Iqp.shape[0])])
    np.savetxt(saxs_1d_stability_path, data.T, header=header)

    # Save saxs 2D data
    saxs_2d_path = data_dir / "saxs_2d.tif"
    skio.imsave(saxs_2d_path, xf_obj.saxs_2d.astype(np.float32))

    # Save correlation functions
    if "Multitau" in xf_obj.atype:
        qvalues, t_el, g2, g2_err, labels = xf_obj.get_g2_data()
        header = "qbin     :" + " ".join(qvalues.astype(str)) + "\n"
        header += "delay (s):" + " ".join(t_el.astype(str)) + "\n"
        header += "labels   :" + " ".join(labels) + "\n"
        g2_path = data_dir / "g2.txt"
        np.savetxt(g2_path, g2, header=header)
        g2_err_path = data_dir / "g2_err.txt"
        np.savetxt(g2_err_path, g2_err, header=header)

        delays_path = data_dir / "delays.txt"
        np.savetxt(delays_path, t_el, header="Delay times (s)")

        delays_path = data_dir / "qbin_values.txt"
        np.savetxt(delays_path, qvalues, header="q (1/Å)")

    if "Twotime" in xf_obj.atype:
        idxlist, c2_stream = xf_obj.get_twotime_stream()
        num_qbins = len(idxlist)
        for n in range(num_qbins):
            qidx, c2 = next(c2_stream)
            #     c2_val.append(c2)
            #     label.append(xf_obj.get_qbin_label(qidx))  # qidx is one-based
            _c2_path = data_dir / f"c2_{n:04d}.tif"
            skio.imsave(_c2_path, c2.astype(np.float32))

        # Save twotime g2 and g2 segments
        shape = xf_obj.c2_g2.shape
        np.savetxt(
            data_dir / "c2_g2.txt",
            xf_obj.c2_g2,
            header=f"g2 from twotime analysis\nnum_delays [{shape[0]}] x num_qbins [{shape[1]}]",
        )
        shape = xf_obj.c2_g2_segments.shape
        np.savetxt(
            data_dir / "c2_g2_partials.txt",
            xf_obj.c2_g2_segments.reshape(-1, num_qbins),
            header=f"g2 from twotime analysis \n(num_delays[{shape[0]}] x num_segments[{shape[1]}]) x num_qbins[{shape[2]}]",
        )


def convert_xpcs_result(
    fname=None,
    target_dir="html",
    num_img=4,
    dpi=240,
    overwrite=False,
    image_only=False,
    create_image_directory=True,
    save_result=True,
):
    """
    Convert XPCS HDF file to web-viewable format with plots and data exports.

    Processes an XPCS analysis HDF file to generate plots, export data, and
    create HTML summaries for web viewing.

    Parameters
    ----------
    fname : str or Path, optional
        Path to the HDF file to convert. Default is None.
    target_dir : str, optional
        Base output directory for generated files. A subdirectory named after
        the HDF file (without extension) will be created within this directory.
        Default is 'html'.
    num_img : int, optional
        Number of correlation function plots per row in the output. Default is 4.
    dpi : int, optional
        Resolution (dots per inch) for generated plots. Higher values produce
        higher quality images but larger file sizes. Default is 240.
    overwrite : bool, optional
        If True, overwrite existing output directory. If False, skip conversion
        if output directory already exists. Default is False.
    image_only : bool, optional
        If True, generate only images without HTML files (useful for Globus
        workflows). If False, generate both images and HTML. Default is False.
    create_image_directory : bool, optional
        If True, create a subdirectory based on the HDF filename. Useful when
        processing multiple files to the same target_dir to avoid overwrites.
        If target_dir is absolute, this can be set to False. Default is True.
    save_result : bool, optional
        If True, save XPCS result data files (SAXS, g2, twotime) to disk.
        If False, skip saving data files and only generate plots and HTML.
        Default is True.

    Returns
    -------
    bool
        True if conversion was successful, False otherwise.

    Notes
    -----
    The function creates a directory structure:
    target_dir/
        filename_stem/
            data/       # Exported data files
            figs/       # Generated plots
            metadata/   # Metadata files
            summary.html  # HTML summary (if image_only=False)

    See Also
    --------
    save_xpcs_result : Save data to files
    plot_xpcs_result : Generate plots
    convert_xpcs_result_safe : Safe wrapper with exception handling

    Examples
    --------
    >>> convert_xpcs_result('data.hdf', target_dir='output', dpi=300)
    True
    """
    fname = Path(fname)

    if not fname.is_file():
        logger.error(f"check {fname}")
        return False

    basename = fname.name
    rel_dir = fname.stem

    top_dir = Path(target_dir) / rel_dir

    if not overwrite and top_dir.is_dir():
        logger.info(f"skip job to avoid overwrite: [{basename}]")
        return False
    top_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    xf_obj = XF(fname)
    try:
        if save_result:
            save_xpcs_result(xf_obj, top_dir)
        plot_xpcs_result(
            xf_obj,
            top_dir,
            num_img=num_img,
            dpi=dpi,
            image_only=image_only,
        )
    except Exception:
        logger.info(f"job failed: [{basename}]")
        traceback.print_exc()
        return False

    t1 = time.perf_counter()
    logger.info(f"job done: [{basename}] in {t1 - t0} seconds")
    return True


def plot_xpcs_result(
    xf_obj,
    top_dir,
    num_img=4,
    dpi=240,
    image_only=False,
):
    """
    Generate plots and HTML summary from XPCS file object.

    Creates visualization plots for SAXS patterns, stability analysis, and
    correlation functions, then generates an HTML summary page.

    Parameters
    ----------
    xf_obj : XpcsFile
        XPCS file object containing analysis results.
    top_dir : Path
        Top-level directory where plots and HTML will be saved.
    num_img : int, optional
        Number of correlation function plots per row. Default is 4.
    dpi : int, optional
        Resolution (dots per inch) for generated plots. Default is 240.
    image_only : bool, optional
        If True, generate only images and rename them for Globus compatibility.
        If False, generate HTML summary page. Default is False.

    Returns
    -------
    bool
        Always returns True upon successful completion.

    Notes
    -----
    Generated plots include:
    - SAXS pattern with mask and q-map
    - Stability plots (intensity vs time)
    - Multitau correlation functions (if available)
    - Twotime correlation maps (if available)
    
    The function also saves metadata in JSON, text, and Excel formats.

    See Also
    --------
    save_xpcs_result : Save raw data to files
    convert_xpcs_result : Main conversion function
    plot_crop_mask_saxs : Plot SAXS pattern with mask
    plot_stability : Plot stability analysis
    plot_multitau_correlation : Plot multitau correlation functions
    plot_twotime_correlation : Plot twotime correlation maps
    """
    figs_dir = top_dir / "figs"
    figs_dir.mkdir(parents=True, exist_ok=True)

    mask, dqmap = plot_crop_mask_saxs(
        xf_obj.mask, xf_obj.saxs_2d, xf_obj.dqmap, figs_dir, dpi=dpi
    )
    # update mask and dqmap with cropped version
    xf_obj.mask = mask
    xf_obj.dqmap = dqmap

    html_dict = {"scattering": str(Path(figs_dir.name) / "saxs_mask.png")}

    img_description = plot_stability(
        xf_obj.sqlist, xf_obj.Iqp, xf_obj.Int_t, figs_dir, dpi=dpi
    )

    html_dict.update(img_description)

    if "Multitau" in xf_obj.atype:
        img_description = plot_multitau_correlation(xf_obj, figs_dir, num_img, dpi)
        html_dict.update(img_description)
    if "Twotime" in xf_obj.atype:
        img_description = plot_twotime_correlation(xf_obj, figs_dir, num_img, dpi)
        html_dict.update(img_description)

    # prepare metadata
    metadata = xf_obj.get_hdf_info()
    metadata["analysis_type"] = xf_obj.atype
    metadata["start_time"] = xf_obj.start_time
    metadata["plot_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = convert_to_native_format(metadata)

    save_metadata(metadata, top_dir)
    html_dict.update({"metadata": metadata})

    # only plot images, not to generate webpage;
    if not image_only:
        # running on local machine
        convert_to_html(top_dir, html_dict)
    else:
        # running on globus
        rename_files(top_dir)

    return True


def convert_xpcs_result_safe(*args, **kwargs):
    """
    Safe wrapper for convert_xpcs_result with exception handling.

    Catches and logs any exceptions that occur during conversion, preventing
    crashes in batch processing scenarios.

    Parameters
    ----------
    *args : tuple
        Positional arguments to pass to convert_xpcs_result.
    **kwargs : dict
        Keyword arguments to pass to convert_xpcs_result.

    Returns
    -------
    bool or None
        True if conversion was successful, False if it failed gracefully,
        or None if an exception occurred.

    See Also
    --------
    convert_xpcs_result : The underlying conversion function
    convert_xpcs_result_wrap : Wrapper for multiprocessing.starmap

    Examples
    --------
    >>> convert_xpcs_result_safe('data.hdf', target_dir='output')
    True
    """
    try:
        x = convert_xpcs_result(*args, **kwargs)
    except Exception:
        basename = Path(args[0]).name
        logger.info(f"job failed: [{basename}]")
        traceback.print_exc()
    else:
        return x


def convert_xpcs_result_wrap(args, kwargs):
    """
    Wrapper function for multiprocessing.starmap compatibility.

    Unpacks arguments and keyword arguments for use with multiprocessing.starmap,
    which requires a specific calling signature.

    Parameters
    ----------
    args : tuple
        Positional arguments to pass to convert_xpcs_result_safe.
    kwargs : dict
        Keyword arguments to pass to convert_xpcs_result_safe.

    Returns
    -------
    bool or None
        Return value from convert_xpcs_result_safe.

    See Also
    --------
    convert_xpcs_result_safe : The underlying safe conversion function
    convert_many_files : Uses this wrapper for parallel processing

    Notes
    -----
    This function is specifically designed for use with multiprocessing.Pool.starmap,
    which requires arguments to be passed as separate tuples.
    """
    return convert_xpcs_result_safe(*args, **kwargs)
