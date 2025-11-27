import logging
import time
import traceback
from datetime import datetime
from pathlib import Path

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


def convert_xpcs_result(
    fname=None,
    target_dir="html",
    num_img=4,
    dpi=240,
    overwrite=False,
    image_only=False,
    create_image_directory=True,
):
    """
    create_image_directory: whether to create a image directory based on the
    hdf filename. It"s useful when plot multiples of hdf files and use the
    same target_dir, so that the images won"t be overwritten. If target_dir is
    absolute, then create_image_directory can be set to False.
    """
    t_start = time.perf_counter()
    fname = Path(fname)

    if not fname.is_file():
        logger.error(f"check {fname}")
        return False

    basename = fname.name
    rel_dir = fname.stem

    top_dir = Path(target_dir) / rel_dir
    figs_dir = top_dir / "figs"
    meta_dir = top_dir / "metadata"
    data_dir = top_dir / "data"

    if not overwrite and top_dir.is_dir():
        logger.info(f"skip job to avoid overwrite: [{basename}]")
        return False

    for d in [top_dir, figs_dir, meta_dir, data_dir]:
        d.mkdir(parents=True, exist_ok=True)

    xf = XF(fname)
    mask, dqmap = plot_crop_mask_saxs(xf.mask, xf.saxs_2d, xf.dqmap, figs_dir, dpi=dpi)
    # update mask and dqmap with cropped version
    xf.mask = mask
    xf.dqmap = dqmap

    html_dict = {"scattering": str(Path(figs_dir.name) / "saxs_mask.png")}

    img_description = plot_stability(xf.sqlist, xf.Iqp, xf.Int_t, figs_dir, dpi=dpi)

    html_dict.update(img_description)

    if "Multitau" in xf.atype:
        img_description = plot_multitau_correlation(xf, figs_dir, num_img, dpi)
        html_dict.update(img_description)
    if "Twotime" in xf.atype:
        img_description = plot_twotime_correlation(xf, figs_dir, num_img, dpi)
        html_dict.update(img_description)

    # prepare metadata
    metadata = xf.get_hdf_info()
    metadata["analysis_type"] = xf.atype
    metadata["start_time"] = xf.start_time
    metadata["plot_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = convert_to_native_format(metadata)

    save_metadata(metadata, meta_dir)
    html_dict.update({"metadata": metadata})

    # only plot images, not to generate webpage;
    if not image_only:
        # running on local machine
        convert_to_html(top_dir, html_dict)
    else:
        # running on globus
        rename_files(top_dir)

    tot_time = round(time.perf_counter() - t_start, 3)
    logger.info(f"job finished in {tot_time}s: [{basename}]")
    return True


def convert_xpcs_result_safe(*args, **kwargs):
    try:
        x = convert_xpcs_result(*args, **kwargs)
    except Exception:
        basename = Path(args[0]).name
        logger.info(f"job failed: [{basename}]")
        traceback.print_exc()
    else:
        return x


def convert_xpcs_result_wrap(args, kwargs):
    # needed for multiprocessing.starmap
    return convert_xpcs_result_safe(*args, **kwargs)
