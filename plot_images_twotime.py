import numpy as np
import skimage.io as skio
import h5py
import os
import matplotlib.pyplot as plt
import jinja2
from multiprocessing import Pool
import glob2
import time
from mpl_toolkits.axes_grid1 import make_axes_locatable


key_map = {
    "saxs_1d": "/exchange/partition-mean-total",
    "saxs_2d": "/exchange/pixelSum",
    "Iqp": "/exchange/partition-mean-partial",
    "dqmap": "/xpcs/dqmap",
    "mask": "/xpcs/mask",
    "t0": "/measurement/instrument/detector/exposure_period",
    # "t1": "/measurement/instrument/detector/exposure_time",
    "avg_frames": "/xpcs/avg_frames",
    "stride_frames": "/xpcs/stride_frames",
}


def find_min_max(x, pmin=1, pmax=99):
    xf = x.ravel()
    vmin = np.percentile(xf, pmin)
    vmax = np.percentile(xf, pmax)
    return vmin, vmax


def plot_twotime_list(deltat, x, label, roi_mask, save_name, save_dir,
                      num_img=4):
    if num_img == 4:
        figsize = (16, 2.5)
    elif num_img == 5:
        figsize = (16, 2)
    else:
        raise ValueError('num_img != 4 hasnot been tested yet')

    fig, ax = plt.subplots(1, num_img + 1, figsize=figsize)

    im0 = ax[0].imshow(roi_mask, origin='lower', cmap=plt.cm.gray)
    fig.colorbar(im0, ax=ax[0])
    ax[0].set_title('q-selection')

    extent = [0, float(x[0].shape[1] * deltat),
              0, float(x[0].shape[0] * deltat)]
    for n in range(len(x)):
        vmin, vmax = find_min_max(x[n])
        imx = ax[n + 1].imshow(x[n], origin='lower', cmap=plt.cm.jet, vmin=vmin,
                               vmax=vmax, extent=extent, interpolation=None)
        ax[n + 1].set_xlabel('t1 (s)')
        ax[n + 1].set_ylabel('t2 (s)')
        fig.colorbar(imx, ax=ax[n + 1])
        ax[n + 1].set_title(label[n])

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, save_name), dpi=240)
    plt.close(fig)


def crop_mask_saxs(mask, saxs, dqmap, save_dir):
    nonzero = np.nonzero(mask)
    sl_v = slice(np.min(nonzero[0]), np.max(nonzero[0]) + 1)
    sl_h = slice(np.min(nonzero[1]), np.max(nonzero[1]) + 1)
    mask = mask[sl_v, sl_h]
    saxs = saxs[sl_v, sl_h]
    dqmap = dqmap[sl_v, sl_h]

    # plot
    fig, ax = plt.subplots(1, 2, figsize=(8, 2.8))
    saxs_min = np.min(saxs[saxs > 0])
    saxs[saxs < saxs_min] = saxs_min
    saxs = np.log10(saxs)

    if saxs.shape[0] <= saxs.shape[1]:
        print('rotate')
        saxs = saxs.T
        mask = mask.T

    im0 = ax[0].imshow(saxs, origin='lower', cmap=plt.cm.jet,
                       interpolation=None)
    fig.colorbar(im0, ax=ax[0])

    im1 = ax[1].imshow(mask, origin='lower', cmap=plt.cm.jet)
    fig.colorbar(im1, ax=ax[1])

    plt.savefig(os.path.join(save_dir, 'saxs_mask.png'), dpi=300)
    plt.close(fig)

    return mask, saxs, dqmap


def convert_to_html(title, data_dict):
    outputfile = title + '.html'

    subs = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template.html').render(title=title, mydata=data_dict)

    # lets write the substitution to a file
    with open(outputfile, 'w') as f:
        f.write(subs)


def convert_one_twotime(fname,
        prefix='/home/8ididata/2021-3/xmlin202112/cluster_results'):

    save_dir = os.path.splitext(fname)[0]
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    result = {}
    with h5py.File(os.path.join(prefix, fname), 'r') as f:
        for key, real_key in key_map.items():
            result[key] = f[real_key][()]

        for n in range(1, 8193):
            real_key = f"/exchange/C2T_all/g2_{n:05d}"
            if real_key in f:
                c2_half = f[real_key][()]
                c2 = c2_half + c2_half.T
                c2_half[np.diag_indices(c2_half.shape[0])] /= 2.0
                result[real_key] = c2
            else:
                break

    deltat = result['t0'] * result['avg_frames'] * result['stride_frames']
    mask, saxs, dqmap = crop_mask_saxs(result['mask'], result['saxs_2d'],
                                       result['dqmap'], save_dir)

    html_dict = {'saxs_mask': os.path.join(save_dir, 'saxs_mask.png')}

    num_img = 4
    xlist = []
    label = []
    roi_mask = np.copy(mask).astype(np.int64)
    last_key = list(result.items())[-1][0]

    for key, val in result.items():
        if len(xlist) == num_img or key == last_key:
            save_name = label[0] + '-' + label[-1] + '.png'
            plot_twotime_list(deltat, xlist, label, roi_mask, save_name,
                              save_dir, num_img=num_img)
            xlist = []
            label = []
            roi_mask = np.copy(mask).astype(np.int64)
            html_dict[key] = os.path.join(save_dir, save_name)

        if not "/exchange/C2T_all/g2_" in key:
            continue
        else:
            qidx = int(key[-5:])
            xlist.append(val)
            label.append(os.path.basename(key))
            roi_mask += (dqmap == qidx) * (len(xlist) + 1)

    convert_to_html(save_dir, html_dict)


def combine_all_htmls(target_folder='web_data'):
    files = os.listdir(target_folder)
    htmls = [x for x in files if x.endswith('.html')]
    htmls.sort()
    htmls_dict = {}

    for x in htmls:
        print(x, target_folder)
        htmls_dict[os.path.splitext(x)[0]] = os.path.join(target_folder, x)

    title = 'cluster_results'
    outputfile = title + '.html'

    subs = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template2.html').render(
        title=title, mydata=htmls_dict)
    # lets write the substitution to a file
    with open(outputfile, 'w') as f:
        f.write(subs)


def convert_all_files():
    # convert('E023_SiO2_111921_270nm_Exp1_IntriDyn_Pos3_XPCS_03_att02_Lq1_001_0001-0500_Twotime.hdf')
    prefix = '/home/8ididata/2021-3/xmlin202112/cluster_results'
    all_tt_raw = glob2.glob(prefix + '/*_Twotime.hdf')
    all_tt = [os.path.basename(x) for x in all_tt_raw]

    # all_tt_raw = []
    # with open('filelists_new.txt', 'r') as f:
    #     for line in f:
    #         all_tt_raw.append(line[:-1])
    # all_tt = all_tt_raw
    all_tt.sort()

    func = lambda x: convert_one_twotime(x, prefix=prefix)
    # # parallel
    # p = Pool(24)
    # p.map(convert_one_twotime, all_tt)

    # one by one
    for x in all_tt:
        t0 = time.perf_counter()
        func(x)
        print(time.perf_counter() - t0, x)
        break



def make_twotime_plots(**event):
    prefix = event['proc_dir']
    fname = event['hdf_file']
    convert_one_twotime(fname, prefix)


def test_plots():
    # twotime
    prefix = '/home/8ididata/2021-3/xmlin202112/cluster_results'
    fname = 'E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    convert_one_twotime(fname, prefix)


if __name__ == '__main__':
    # combine_all_htmls()
    # convert_all_files()
    test_plots()
