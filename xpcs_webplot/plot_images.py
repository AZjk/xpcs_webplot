import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from multiprocessing import Pool
import time
import json
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .html_utlits import convert_to_html
import logging
import traceback
from pyxpcsviewer.xpcs_file import XpcsFile as XF
import matplotlib.colors as mcolors

colors = [
    [1.0, 1.0, 1.0,  0.6],   # White (first bin)
    [0.55, 0.0, 0.0, 0.6],  # Dark Red
    [0.0, 0.39, 0.0, 0.6],  # Dark Green
    [0.0, 0.0, 0.55, 0.6],  # Dark Blue
    [0.55, 0.0, 0.55,0.6]  # Dark Magenta
]
cmap_4colors = mcolors.ListedColormap(colors)


logger = logging.getLogger(__name__)


def rename_files(work_dir):
    """
    rename the png files in work_dir so that they follow the convention defined
    in globus webportal.
    """
    os.chdir(work_dir)
    all_png = os.listdir(".")
    all_png = [x for x in all_png if x.endswith(".png")]

    if "saxs_mask.png" in all_png:
        os.rename("saxs_mask.png", "scattering_pattern_log.png")
    if "stability.png" in all_png:
        os.rename("stability.png", "total_intensity_vs_time.png")

    # clean work_dir
    basename_str = os.path.basename(work_dir)

    for n in range(1024):
        g2_name = "g2_%04d.png" % n
        if g2_name in all_png:
            os.rename(g2_name,
                basename_str + "_g2_corr_%03d_%03d.png" % (n * 9, n * 9 + 8))
        else:
            break

    offset = n
    for n in range(1024):
        g2_name = "c2_%04d.png" % n
        if g2_name in all_png:
            m = n + offset
            os.rename(g2_name,
                basename_str + "_g2_corr_%03d_%03d.png" % (m * 9, m * 9 + 8))
        else:
            break

    return



def check_exist(basename, target_dir):
    fname_no_ext = os.path.splitext(basename)[0]
    if os.path.isfile(os.path.join(target_dir, fname_no_ext + ".html")):
        return True
    else:
        return False


def plot_stability(ql_sta, Iqp, intt, save_dir=".", dpi=240):
    if ql_sta.ndim == 2:
        ql_sta = np.squeeze(ql_sta)

    figsize = (16, 3.6)
    fig, ax = plt.subplots(1, 2, figsize=figsize)

    for n in range(Iqp.shape[0]):
        ax[0].loglog(ql_sta, Iqp[n], label=f"{n}")

    ax[0].set_xlabel("$q (\\AA^{-1})$")
    ax[0].set_ylabel("Intensity (photons/pixel)")
    ax[0].set_title("Partial mean")
    ax[0].legend()

    # t_axis = np.arange(intt.shape[0]) * deltat
    ax[1].plot(intt[0], intt[1], "b", linewidth=0.2)
    ax[1].set_xlabel("frame index")
    ax[1].set_ylabel("Intensity (photons/pixel/frame)")
    ax[1].set_title("Intensity vs t")
    plt.tight_layout()

    save_name = os.path.join(save_dir, "stability.png")
    plt.savefig(save_name, dpi=dpi)
    plt.close(fig)

    img_description = {
        "stability": os.path.join(os.path.basename(save_dir), "stability.png")
    }

    return img_description


def find_min_max(x, pmin=1, pmax=99):
    xf = x.ravel()
    vmin = np.percentile(xf, pmin)
    vmax = np.percentile(xf, pmax)
    return vmin, vmax


def plot_roi_mask(fig, ax, roi_mask, num_img, nophi=1):
    assert roi_mask.ndim == 2
    invalid_idx = roi_mask < 2

    if nophi == 1:
        valid_roi = roi_mask == 1
        roi_mask = roi_mask.astype(np.float32)
        roi_mask -= 1
        roi_mask[invalid_idx] = np.nan
        # mark the overall valid region with light color;
        roi_mask[valid_roi] = 0.25
        im = ax.imshow(roi_mask, origin="lower", cmap=cmap_4colors,
                       vmin=0, vmax=num_img + 1)
    else:
        s = np.ones_like(roi_mask, dtype=np.float32)
        h = roi_mask % nophi
        h = (h - np.min(h)) / (np.max(h) - np.min(h))
        v = roi_mask // nophi
        v = 1 - (v - np.min(v)) / (np.max(v) - np.min(v))
        roi_mask = hsv_to_rgb(np.dstack((h, s, v)))
        roi_mask[invalid_idx] = np.nan
        im = ax.imshow(roi_mask)

    divider0 = make_axes_locatable(ax)
    cax = divider0.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax)
    ax.set_title("q-selection")
    return


def plot_multitau_row(xf_obj, roi_mask, save_name, save_dir, num_img=4, dpi=240,
                      q_index_offset=0):

    figsize = (16, 12 / (num_img + 1))
    fig, ax = plt.subplots(1, num_img + 1, figsize=figsize)

    shape = xf_obj.dynamic_num_pts
    plot_roi_mask(fig, ax[0], roi_mask, num_img, shape[1])

    cmap = plt.cm.get_cmap("hsv")
    for n in range(num_img):
        q_index = n + q_index_offset
        if q_index >= shape[0]:
            continue
        bx = ax[n + 1]
        qbin_list = xf_obj.get_qbinlist_at_qindex(q_index, zero_based=True)
        for p, qbin in enumerate(qbin_list):
            if shape[1] == 1:
                color = "b"
                title = xf_obj.get_qbin_label(qbin + 1)
                label = f"qbin={qbin+1}"
            else:
                color = cmap(p / shape[1])
                label_full = xf_obj.get_qbin_label(qbin + 1)
                label_q = label_full.split(", ")[0]
                label = f"{qbin+1}: " + label_full.split(", ")[1]
                title = label_q

            g2_temp = xf_obj.g2[:, qbin]
            bx.semilogx(xf_obj.t_el, g2_temp, "o", color=color, mfc="none", ms=2.0,
                        alpha=0.8, label=label)
            bx.semilogx(xf_obj.t_el, g2_temp, color=color, alpha=0.8, lw=0.5)

            if p == 0:
                bx.set_xlabel("t (s)")
                bx.set_ylabel("g2")
                bx.set_title(title)
        bx.legend(loc="best", fontsize=6)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, save_name), dpi=dpi)
    plt.close(fig)


def plot_twotime_row(deltat, x, label, roi_mask, save_name, save_dir,
                     num_img=4, dpi=240):

    figsize = (16, 12 / (num_img))
    fig, ax = plt.subplots(1, num_img + 1, figsize=figsize)

    plot_roi_mask(fig, ax[0], roi_mask, num_img)

    extent = [0, float(x[0].shape[1] * deltat),
              0, float(x[0].shape[0] * deltat)]
    for n in range(len(x)):
        vmin, vmax = find_min_max(x[n])
        imx = ax[n + 1].imshow(x[n], origin="lower", cmap=plt.cm.jet, vmin=vmin,
                               vmax=vmax, extent=extent, interpolation=None)
        ax[n + 1].set_xlabel("t1 (s)")
        ax[n + 1].set_ylabel("t2 (s)")
        divider0 = make_axes_locatable(ax[n + 1])
        cax = divider0.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(imx, cax=cax)
        ax[n + 1].set_title(label[n])

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, save_name), dpi=dpi)
    plt.close(fig)


def plot_crop_mask_saxs(mask, saxs, dqmap, save_dir, dpi=120):
    figsize = (16, 3.6)
    fig, ax = plt.subplots(1, 2, figsize=figsize)
    if saxs.ndim == 3:
        saxs = np.squeeze(saxs)
    nonzero = np.nonzero(mask)
    sl_v = slice(np.min(nonzero[0]), np.max(nonzero[0]) + 1)
    sl_h = slice(np.min(nonzero[1]), np.max(nonzero[1]) + 1)

    # in some cases qmap and mask are rotated.
    if mask.shape != saxs.shape:
        saxs = saxs.T

    mask = mask[sl_v, sl_h]
    saxs = saxs[sl_v, sl_h] * mask
    dqmap = dqmap[sl_v, sl_h] * mask

    # plot
    valid_mask = saxs > 0
    if np.sum(valid_mask) == 0:
        logger.error("No valid data in saxs")
    else:
        saxs_min = np.min(saxs[saxs > 0])
        saxs[saxs < saxs_min] = saxs_min
        saxs = np.log10(saxs)

    if saxs.shape[0] > saxs.shape[1]:
        saxs = saxs.T
        mask = mask.T
        dqmap = dqmap.T

    vmin, vmax = find_min_max(saxs, 1, 99.9)
    im0 = ax[0].imshow(saxs, origin="lower", cmap=plt.cm.jet,
                       interpolation=None, vmin=vmin, vmax=vmax)
    ax[0].set_title("Scattering pattern")
    divider0 = make_axes_locatable(ax[0])
    cax0 = divider0.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im0, cax=cax0)

    im1 = ax[1].imshow(dqmap, origin="lower", cmap=plt.cm.jet,
                       interpolation=None)
    ax[1].set_title("Dynamic qmap")
    divider1 = make_axes_locatable(ax[1])
    cax1 = divider1.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im1, cax=cax1)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "saxs_mask.png"), dpi=dpi)
    plt.close(fig)

    return mask, dqmap


def create_highlight_roi_mask(xf_obj, st, ed):
    roi_mask = np.copy(xf_obj.mask).astype(np.int64)
    for idx in range(st, ed):
        val = (idx - st)  + 1
        roi_mask += (xf_obj.dqmap == (idx + 1)) * val
    return roi_mask


def plot_multitau_correlation(xf_obj, save_dir, num_img, dpi=120):
    shape = xf_obj.dynamic_num_pts
    tot_num = shape[0]
    img_list = []
    num_row = (tot_num + num_img - 1) // num_img
    if num_row == 1: num_img = shape[0]

    for n in range(0, num_row):
        st = num_img * n
        ed = min(tot_num, num_img * (n + 1))
        save_name = f"g2_{n:04d}.png"
        roi_mask = create_highlight_roi_mask(xf_obj, st, ed)
        plot_multitau_row(xf_obj, roi_mask, save_name, save_dir,
                          num_img=num_img, dpi=dpi, q_index_offset=st)
        img_list.append(os.path.join(os.path.basename(save_dir), save_name))

    return {"correlation_g2": img_list}


def plot_twotime_correlation(xf_obj, save_dir, num_img, dpi=120):
    img_list = []
    idxlist, c2_stream = xf_obj.get_twotime_stream()
    tot_num = len(idxlist)

    num_row = (tot_num + num_img - 1) // num_img
    if num_row == 1:
        num_img = tot_num

    for n in range(0, num_row):
        st = num_img * n
        ed = min(tot_num, num_img * (n + 1))
        save_name = f"c2_{n:04d}.png"
        c2_val = []
        label = []
        roi_mask = create_highlight_roi_mask(xf_obj, st, ed)
        for idx in range(st, ed):
            qidx, c2 = next(c2_stream)
            c2_val.append(c2)
            label.append(xf_obj.get_qbin_label(qidx))   # qidx is one-based

        plot_twotime_row(xf_obj.t0, c2_val, label, roi_mask,
                        save_name, save_dir, num_img=num_img, dpi=dpi)

        img_list.append(os.path.join(os.path.basename(save_dir), save_name))

    return {"correlation_c2": img_list}



class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy data types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):  # Handle NumPy boolean
            return bool(obj)
        return super().default(obj)  # Use default method for other types



def hdf2web(fname=None, target_dir="html", num_img=4, dpi=240, overwrite=False,
            image_only=False, create_image_directory=True):
    """
    create_image_directory: whether to create a image directory based on the
    hdf filename. It"s useful when plot multiples of hdf files and use the
    same target_dir, so that the images won"t be overwritten. If target_dir is
    absolute, then create_image_directory can be set to False.
    """
    t_start = time.perf_counter()
    if fname is None or not os.path.isfile(fname):
        logger.error(f"check {fname}")
        return False

    basename = os.path.basename(fname)
    save_dir_rel = os.path.splitext(basename)[0]
    if create_image_directory:
        save_dir = os.path.join(target_dir, save_dir_rel)
    else:
        save_dir = target_dir

    if not overwrite and os.path.isdir(save_dir):
        logger.info(f"skip job to avoid overwrite: [{basename}]")
        return False

    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    xf = XF(fname)

    mask, dqmap = plot_crop_mask_saxs(xf.mask, xf.saxs_2d, xf.dqmap,
                                      save_dir, dpi=dpi)
    # update mask and dqmap with cropped version
    xf.mask = mask
    xf.dqmap = dqmap

    html_dict = {"scattering": os.path.join(save_dir_rel, "saxs_mask.png")}

    img_description = plot_stability(xf.sqlist, xf.Iqp, xf.Int_t, save_dir,
                                     dpi=dpi)

    html_dict.update(img_description)

    if "Multitau" in xf.atype:
        img_description = plot_multitau_correlation(xf, save_dir, num_img, dpi)
        html_dict.update(img_description)
    if "Twotime" in xf.atype:
        img_description = plot_twotime_correlation(xf, save_dir, num_img, dpi)
        html_dict.update(img_description)

    # prepare metadata
    metadata = xf.get_hdf_info()
    metadata["analysis_type"] = xf.atype
    metadata["start_time"] = xf.start_time
    metadata["plot_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(os.path.join(save_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4, cls=NpEncoder)

    html_dict.update({"metadata": metadata})

    # only plot images, not to generate webpage;
    if not image_only:
        # running on local machine
        convert_to_html(save_dir, html_dict)
    else:
        # running on globus
        rename_files(save_dir)

    tot_time = round(time.perf_counter() - t_start, 3)
    logger.info(f"job finished in {tot_time}s: [{basename}]")
    return True


def hdf2web_safe(*args, **kwargs):
    try:
        x = hdf2web(*args, **kwargs)
    except Exception:
        basename = os.path.basename(args[0])
        logger.info(f"job failed: [{basename}]")
        traceback.print_exc()
    else:
        return x


def hdf2web_safe_wrap(args, kwargs):
    # needed for multiprocessing.starmap
    return hdf2web_safe(*args, **kwargs)


def convert_many_files(flist, num_workers=24, target_dir="html", **kwargs):

    args = list(zip(flist, [target_dir] * len(flist)))
    p = Pool(num_workers)
    # p.map(convert_hdf_webpage, flist)
    p.starmap(hdf2web_safe, args)


if __name__ == "__main__":
    # test_plots()
    # test_parallel()
    rename_files("/clhome/MQICHU/html/A056_Ludox15_att00_L2M_quiescent_001_0001-0300")
