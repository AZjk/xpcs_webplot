import numpy as np
import h5py
import os
import matplotlib.pyplot as plt
from multiprocessing import Pool
import glob2
import time
import json
from mpl_toolkits.axes_grid1 import make_axes_locatable
from html_utlits import convert_to_html
import logging
import traceback
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


key_map = {
    "saxs_1d": "/exchange/partition-mean-total",
    "Iqp": "/exchange/partition-mean-partial",
    "ql_sta": "/xpcs/sqlist",
    "ql_dyn": "/xpcs/dqlist",
    "dqmap": "/xpcs/dqmap",
    "sqmap": "/xpcs/sqmap",
    "mask": "/xpcs/mask",
    "type": "/xpcs/analysis_type",
    "t0": "/measurement/instrument/detector/exposure_period",
    "t1": "/measurement/instrument/detector/exposure_time",
    "tau": "/exchange/tau",
    "g2": "/exchange/norm-0-g2",
    "g2_err": "/exchange/norm-0-stderr",
    "saxs_2d": "/exchange/pixelSum",
    "Int_t": "/exchange/frameSum",
    "avg_frames": "/xpcs/avg_frames",
    "stride_frames": "/xpcs/stride_frames",
    "sphilist": "/xpcs/sphilist",
    "t_begin": "/measurement/instrument/source_begin/datetime",
    "t_end": "/measurement/instrument/source_end/datetime",
    "temperature_a_rbv": "/measurement/sample/temperature_A",
    "temperature_a_set": "/measurement/sample/temperature_A_set",
    "temperature_b_rbv": "/measurement/sample/temperature_B",
    "temperature_b_set": "/measurement/sample/temperature_B_set",
    "current": "/measurement/instrument/source_begin/current",
}


def get(hdf_handler, key):
    if key_map[key] not in hdf_handler:
        return 'None'
    val = hdf_handler.get(key_map[key])[()]
    if type(val) in [np.bytes_, bytes]:
        val = val.decode()
    if isinstance(val, np.ndarray):
        if val.size == 1:
            val = float(val)
            if abs(val) > 1e-2:
                val = round(val, 4)
    return val


def get_anaylsis_type(hdf_fname):
    try:
        with h5py.File(hdf_fname, 'r') as f:
            atype = f.get('/xpcs/analysis_type')[()].decode().capitalize()
    except Exception:
        return None
    return atype


def check_exist(basename, target_dir):
    fname_no_ext = os.path.splitext(basename)[0]
    if os.path.isfile(os.path.join(target_dir, fname_no_ext + '.html')):
        return True
    else:
        return False


def plot_stability(ql_sta, Iqp, intt, save_dir='.', dpi=240):

    figsize = (16, 3.6)
    fig, ax = plt.subplots(1, 2, figsize=figsize)
    
    # some problem with missing qvals
    min_dim = min(ql_sta.shape[1], Iqp.shape[1])
    sl = slice(0, min_dim)
    Iqp = Iqp[:, sl]
    q = ql_sta[0, sl]
    for n in range(Iqp.shape[0]):
        ax[0].loglog(q * 1000, Iqp[n], label=f'{n}')

    ax[0].set_xlabel("$q (\\AA^{-1}) \\times 10^3$")
    ax[0].set_ylabel("Intensity (photons/pixel)")
    ax[0].set_title('Partial mean')
    ax[0].legend()

    # t_axis = np.arange(intt.shape[0]) * deltat
    ax[1].plot(intt[0], intt[1], 'b', linewidth=0.2)
    ax[1].set_xlabel("t (s)")
    ax[1].set_ylabel("Intensity (photons/pixel/frame)")
    ax[1].set_title('Intensity vs t')
    plt.tight_layout()

    save_name = os.path.join(save_dir, 'stability.png')
    plt.savefig(save_name, dpi=dpi)
    plt.close(fig)

    img_description = {
        'stability': os.path.join(os.path.basename(save_dir), 'stability.png')
    }

    return img_description


def find_min_max(x, pmin=1, pmax=99):
    xf = x.ravel()
    vmin = np.percentile(xf, pmin)
    vmax = np.percentile(xf, pmax)
    return vmin, vmax


def plot_roi_mask(fig, ax, roi_mask, num_img):
    valid_roi = roi_mask == 1
    roi_mask = roi_mask.astype(np.float32)
    roi_mask[roi_mask < 2] = np.nan
    roi_mask -= 1
    # mark the overall valid region with light color;
    roi_mask[valid_roi] = 0.25
    im = ax.imshow(roi_mask, origin='lower', cmap=plt.get_cmap('Greys'),
                   vmin=0, vmax=num_img + 1)
    divider0 = make_axes_locatable(ax)
    cax = divider0.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax)
    ax.set_title('q-selection')
    return


def plot_multitau_row(t_el, g2, g2_err, roi_mask, save_name, save_dir, label,
                      num_img=4, dpi=240):

    figsize = (16, 12 / (num_img + 1))
    fig, ax = plt.subplots(1, num_img + 1, figsize=figsize)

    plot_roi_mask(fig, ax[0], roi_mask, num_img)

    for n in range(g2.shape[0]):
        bx = ax[n + 1]
        bx.semilogx(t_el, g2[n], 'bo', mfc='none', ms=2.0, alpha=0.8)
        bx.semilogx(t_el, g2[n], 'r', alpha=0.5, lw=0.5)
        # bx.errorbar(t_el, g2[n], yerr=g2_err[n], fmt='o',
        #             ecolor='lightgreen',
        #             color='blue', ms=0.001, mew=1, capsize=3, alpha=0.8)
        # bx.set_xscale('log')
        bx.set_xlabel('t (s)')
        bx.set_ylabel('g2')
        bx.set_title(label[n])

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
        imx = ax[n + 1].imshow(x[n], origin='lower', cmap=plt.cm.jet, vmin=vmin,
                               vmax=vmax, extent=extent, interpolation=None)
        ax[n + 1].set_xlabel('t1 (s)')
        ax[n + 1].set_ylabel('t2 (s)')
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

    nonzero = np.nonzero(mask)
    sl_v = slice(np.min(nonzero[0]), np.max(nonzero[0]) + 1)
    sl_h = slice(np.min(nonzero[1]), np.max(nonzero[1]) + 1)
    mask = mask[sl_v, sl_h]
    saxs = saxs[sl_v, sl_h]
    dqmap = dqmap[sl_v, sl_h]

    # plot
    saxs_min = np.min(saxs[saxs > 0])
    saxs[saxs < saxs_min] = saxs_min
    saxs = np.log10(saxs)

    if saxs.shape[0] > saxs.shape[1]:
        saxs = saxs.T
        mask = mask.T
        dqmap = dqmap.T

    vmin, vmax = find_min_max(saxs, 1, 99.9)
    im0 = ax[0].imshow(saxs, origin='lower', cmap=plt.cm.jet,
                       interpolation=None, vmin=vmin, vmax=vmax)
    ax[0].set_title('Scattering pattern')
    divider0 = make_axes_locatable(ax[0])
    cax0 = divider0.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im0, cax=cax0)

    im1 = ax[1].imshow(dqmap, origin='lower', cmap=plt.cm.jet,
                       interpolation=None)
    ax[1].set_title('Dynamic qmap')
    divider1 = make_axes_locatable(ax[1])
    cax1 = divider1.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im1, cax=cax1)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'saxs_mask.png'), dpi=dpi)
    plt.close(fig)

    return mask, dqmap


def plot_multitau_correlation(info, save_dir, num_img, dpi=120):
    g2d = info['g2'].T
    g2e = info['g2_err'].T
    tot_num = g2d.shape[0]
    img_list = []

    for n in range(0, (tot_num + num_img - 1) // num_img):
        st = num_img * n
        ed = min(tot_num, num_img * (n + 1))
        save_name = f'g2_{n:04d}.png'
        label = []
        roi_mask = np.copy(info['mask']).astype(np.int64)
        for idx in range(st, ed):
            label.append('$q=%.4f\\AA^{-1}$' % info['ql_dyn'][0, idx])
            roi_mask += (info['dqmap'] == (idx + 1)) * (idx - st + 1)

        plot_multitau_row(info['t_el'][0], g2d[st:ed], g2e[st:ed], roi_mask,
                          save_name, save_dir, label, num_img, dpi)

        img_list.append(os.path.join(os.path.basename(save_dir), save_name))

    return {'correlation': img_list}



def plot_twotime_correlation(info, save_dir, num_img, dpi=120):
    c2_val = info['c2_val']
    c2_key = info['c2_key']
    tot_num = len(c2_key) 
    img_list = []

    for n in range(0, (tot_num + num_img - 1) // num_img):
        st = num_img * n
        ed = min(tot_num, num_img * (n + 1))
        save_name = f'c2_{n:04d}.png'
        label = []
        roi_mask = np.copy(info['mask']).astype(np.int64)
        for idx in range(st, ed):
            label.append(f'c2_{c2_key[idx]:04d}')
            roi_mask += (info['dqmap'] == (idx + 1)) * (idx - st + 1)

        plot_twotime_row(info['delta_t'], c2_val[st:ed], label, roi_mask,
                        save_name, save_dir, num_img=num_img, dpi=dpi)

        img_list.append(os.path.join(os.path.basename(save_dir), save_name))

    return {'correlation': img_list}


def convert_hdf_webpage(fname, target_dir='html', num_img=4, dpi=120,
                        overwrite=False):
    t_start = time.perf_counter()
    basename = os.path.basename(fname)
    save_dir_rel = os.path.splitext(basename)[0]
    if not overwrite and check_exist(basename, target_dir):
        logging.info(f'file has been processed [{basename}].')
        return

    save_dir = os.path.join(target_dir, save_dir_rel)
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    info = {}
    atype = get_anaylsis_type(fname)
    if atype not in ['Twotime', 'Multitau']:
        logging.info(f'cannot read file [{basename}].')
        return

    with h5py.File(fname, 'r') as f:
        for key, real_key in key_map.items():
            if atype == 'Twotime' and key in ['g2', 'g2_err', 'tau']:
                continue
            info[key] = get(f, key)

        if atype == 'Twotime':
            info['c2_val'] = [] 
            info['c2_key'] = []
            all_keys = list(f['/exchange/C2T_all/'])
            for key in all_keys:
                c2_half = f['/exchange/C2T_all/' + key][()]
                c2 = c2_half + c2_half.T
                c2_half[np.diag_indices(c2_half.shape[0])] /= 2.0
                info['c2_val'].append(c2)
                info['c2_key'].append(int(key[3:]))
            info['tau'] = info['c2_val'][0].shape[0]
    delta_t = info['t0'] * info['avg_frames'] * info['stride_frames']
    info['delta_t'] = delta_t
    info['t_el'] = delta_t * info['tau']

    # plot saxs and sqmap
    mask, dqmap = plot_crop_mask_saxs(info['mask'], info['saxs_2d'],
                                      info['dqmap'], save_dir)
    # update the dynamic qmap with a cropped one
    info['dqmap'] = dqmap
    info['mask'] = mask

    html_dict = {'scattering': os.path.join(save_dir_rel, 'saxs_mask.png')}

    img_description = plot_stability(
        info['ql_sta'], info['Iqp'], info['Int_t'], save_dir)
    html_dict.update(img_description)

    if atype == 'Twotime':
        img_description = plot_twotime_correlation(
            info, save_dir, num_img, dpi)
    elif atype == 'Multitau':
        img_description = plot_multitau_correlation(
            info, save_dir, num_img, dpi)
    else:
        raise NotImplementedError

    html_dict.update(img_description)
    metadata = {}
    for key in list(key_map.keys())[-7:]:
        metadata[key] = info[key]
    metadata['analysis_type'] = atype

    with open(os.path.join(save_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)

    html_dict.update({'metadata': metadata})
    convert_to_html(save_dir, html_dict)
    tot_time = round(time.perf_counter() - t_start, 3)
    logging.info(f'finished in [{tot_time}]s: [{basename}]')


def convert_hdf_webpage_wrapper(*args, **kwargs):
    try:
        x = convert_hdf_webpage(*args, **kwargs)
    except Exception as ex:
        basename = os.path.basename(args[0])
        logging.info(f'failed job: [{basename}]')
        traceback.print_exc()
    else:
        return x


def convert_many_files(flist, num_workers=12, mode='parallel',
                       target_dir='html'):
    flist.sort()

    if mode == 'parallel':
        args = list(zip(flist, [target_dir] * len(flist)))
        p = Pool(num_workers)
        # p.map(convert_hdf_webpage, flist)
        p.starmap(convert_hdf_webpage_wrapper, args)
    else:
        for f in flist:
            convert_hdf_webpage(f)


def test_plots():
    # twotime
    # fname = '/home/8ididata/2021-3/xmlin202112/cluster_results/E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    # convert_hdf_webpage(fname)

    # fname = '/local/dev/xpcs_data_raw/cluster_results/N077_D100_att02_0001_0001-100000.hdf'
    # convert_hdf_webpage(fname)

    fname = '/net/wolf/data/xpcs8//2021-3/xmlin202112/cluster_results/E121_SiO2_111921_270nm_62v_Exp3_PostPreshear_Preshear0p01_XPCS_01_007_att02_Lq1_001_0001-0500_Twotime.hdf'
    convert_hdf_webpage(fname)


def test_parallel():
    # prefix = '/home/8ididata/2021-3/xmlin202112/cluster_results'
    # prefix = '/net/wolf/data/xpcs8//2021-3/xmlin202112/cluster_results'
    prefix = '/net/wolf/data/xpcs8/2021-3/foster202110/cluster_results'
    flist = glob2.glob(prefix + '/*.hdf')
    flist.sort()
    flist_twotime = [x for x in flist if 'Twotime' in x]
    for f in flist_twotime:
        flist.remove(f)

    flist_twotime = flist_twotime[0:80] 
    flist = flist[0:80]
    convert_many_files(flist, mode='parallel')
    convert_many_files(flist_twotime, mode='parallel')


if __name__ == '__main__':
    # test_plots()
    test_parallel()
