import glob2
import os
from plot_images import hdf2web_safe as hdf2web
from plot_images import hdf2web_safe_fixed as hdf2web_fixed
import logging
import json
import argparse


# hdf2web(fname, target_dir='html', num_img=4, dpi=240, overwrite=False)


home_dir = os.path.join(os.path.expanduser('~'), '.xpcs_webplot')
if not os.path.isdir(home_dir):
    os.mkdir(home_dir)
config_fname = os.path.join(home_dir, 'default_setting.json')


try:
    with open(config_fname, 'r') as f:
        default_setting = json.load(f)
except Exception:
    default_setting = {
        "dpi": 120,
        "overwrite": False,
        "num_img": 4,
        "target_dir": './'
    }


def convert_many_files(flist, num_workers=24, **kwargs):
    assert isinstance(flist, list)
    setting = default_setting.copy()
    setting.update(kwargs)
    kwargs = setting

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
        flist = glob2.glob(folder + '/*.hdf')
        flist.sort()
        convert_many_files(flist, **kwargs)


def convert_one_file(fname, **kwargs):
    setting = default_setting.copy()
    setting.update(kwargs)
    return hdf2web(fname, **setting)


def update_default_setting(**kwargs):
    setting = default_setting.copy()
    setting.update(kwargs)
    with open(os.path.join(config_fname), 'w') as f:
        json.dump(setting, f, indent=4)


# def generate_random_dir(prefix='/net/wolf/data/xpcs8/2021-3', dry_run=False):
def generate_random_dir(prefix='/local/data_miaoqi/html', dry_run=False):
    import uuid
    new_id = str(uuid.uuid4())[-12:]
    new_dir = os.path.join(prefix, new_id)
    if not dry_run:
        os.mkdir(new_dir)
        update_default_setting(target_dir=new_dir)
        print("new directory is", new_dir)
    else:
        print("dry run: dir is", new_dir)


def test_plots():
    # twotime
    fname = '/net/wolf/data/xpcs8/2021-3/xmlin202112/cluster_results/E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    # fname = '/home/8ididata/2021-3/xmlin202112/cluster_results/E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    convert_one_file(fname, target_dir='html2')

    # fname = '/local/dev/xpcs_data_raw/cluster_results/N077_D100_att02_0001_0001-100000.hdf'
    # convert_hdf_webpage(fname)

    fname = '/net/wolf/data/xpcs8//2021-3/xmlin202112/cluster_results/E121_SiO2_111921_270nm_62v_Exp3_PostPreshear_Preshear0p01_XPCS_01_007_att02_Lq1_001_0001-0500_Twotime.hdf'
    # fname = "/home/8ididata/2021-3/foster202110/cluster_results/B985_2_10k_star_dynamic_0p1Hz_Strain1.05mm_Ampl0.040mm_att5_Lq0_001_0001-0800.hdf"
    convert_one_file(fname, dpi=240, num_img=4)

    # fname = "/net/wolf/data/xpcs8/2021-3/tingxu202111/cluster_results_01_27/F2250_D100_025C_att00_Rq0_00001_0001-100000.hdf"
    # # fndfme = "/home/8ididata/2021-3/tingxu202111/cluster_results_01_27/F2250_D100_025C_att00_Rq0_00001_0001-100000.hdf"
    # convert_hdf_webpage(fname)


parser = argparse.ArgumentParser(description='Convert XPCS hdf result file to webpage')

parser.add_argument('fname', metavar='fname', type=str, help='hdf filename')

parser.add_argument('target_dir', type=str, nargs='?', default= help='output directory')

parser.add_argument('num_img', type=int, default=-1, help='number of images per row')

parser.add_argument('overwrite', type=bool, default=-1, help='overwrite flag')

args = parser.parse_args()

# print(args.accumulate(args.integers))
# hdf2web(fname, target_dir='html', num_img=4, dpi=240, overwrite=False)
print(args)
