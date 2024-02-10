import glob
import os
from .plot_images import hdf2web_safe as hdf2web
from .plot_images import hdf2web_safe_fixed as hdf2web_fixed
from .html_utlits import combine_all_htmls
import json
import sys
import datetime


home_dir = os.path.join(os.path.expanduser('~'), '.xpcs_webplot')
config_fname = os.path.join(home_dir, 'default_setting.json')


def load_setting():
    if not os.path.isdir(home_dir):
        os.mkdir(home_dir)
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
        save_setting(default_setting)
    return default_setting


def save_setting(new_setting):
    with open(config_fname, 'w') as f:
        json.dump(new_setting, f)


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


def update_default_setting(**kwargs):
    setting = load_setting()
    setting.update(kwargs)
    with open(os.path.join(config_fname), 'w') as f:
        json.dump(setting, f, indent=4)


def generate_random_dir(prefix='/net/wolf/data/xpcs8/2022-1/html'):
# def generate_random_dir(prefix='/local/data_miaoqi/html'):
    import uuid
    new_id = str(uuid.uuid4())[-12:]
    new_dir = os.path.join(prefix, new_id)
    print("New random directory is", new_dir)
    flag_str = input('-- create this folder and set it as the target_dir ? [Y/N] ').upper().strip()
    assert flag_str in ['Y', 'N']
    flag = (flag_str == 'Y')
    if flag:
        os.mkdir(new_dir)
        update_default_setting(target_dir=new_dir)
        setting = load_setting()
        print("-- new dir is created and set as the new target_dir.")
        print(json.dumps(setting, indent=4))
    else:
        setting = load_setting()
        print("-- setting not changed.")
        print(json.dumps(setting, indent=4))
    print(f'You may change other settings manually in the file [{config_fname}]')


def test_plots():
    target_dir = 'html2'
    # twotime
    fname = '/net/wolf/data/xpcs8/2021-3/xmlin202112/cluster_results/E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    # fname = '/home/8ididata/2021-3/xmlin202112/cluster_results/E005_SiO2_111921_Exp1_IntriDyn_Pos1_XPCS_00_att02_Lq1_001_0001-0522_Twotime.hdf'
    convert_one_file(fname, target_dir=target_dir)

    # fname = '/local/dev/xpcs_data_raw/cluster_results/N077_D100_att02_0001_0001-100000.hdf'
    # convert_hdf_webpage(fname)

    fname = '/net/wolf/data/xpcs8//2021-3/xmlin202112/cluster_results/E121_SiO2_111921_270nm_62v_Exp3_PostPreshear_Preshear0p01_XPCS_01_007_att02_Lq1_001_0001-0500_Twotime.hdf'
    # fname = "/home/8ididata/2021-3/foster202110/cluster_results/B985_2_10k_star_dynamic_0p1Hz_Strain1.05mm_Ampl0.040mm_att5_Lq0_001_0001-0800.hdf"
    convert_one_file(fname, dpi=240, num_img=4, target_dir=target_dir)

    fname = '/net/wolf/data/xpcs8/2021-3/foster202110/cluster_results/B981_2_10k_star_dynamic_0p1Hz_Strain1.01mm_Ampl0.005mm_att5_Lq0_001_0001-0800.hdf'
    convert_one_file(fname, dpi=240, num_img=4, target_dir=target_dir)

    fname = '/net/wolf/data/xpcs8/2021-3/foster202110/cluster_results/B981_2_10k_star_dynamic_0p1Hz_Strain1.01mm_Ampl0.005mm_att5_Lq0_001_0001-0800_Twotime.hdf'
    convert_one_file(fname, dpi=240, num_img=4, target_dir=target_dir)
    # fname = "/net/wolf/data/xpcs8/2021-3/tingxu202111/cluster_results_01_27/F2250_D100_025C_att00_Rq0_00001_0001-100000.hdf"
    # # fndfme = "/home/8ididata/2021-3/tingxu202111/cluster_results_01_27/F2250_D100_025C_att00_Rq0_00001_0001-100000.hdf"
    # convert_hdf_webpage(fname)


# setting = load_setting()
# parser = argparse.ArgumentParser(description='Convert XPCS hdf result file to webpage')
# 
# parser.add_argument('--fname', '-f', type=str, help='hdf filename or folder. If a folder is passed, every hdf file in it will be converted')
# 
# parser.add_argument('--target_dir', type=str, nargs='?', default=setting['target_dir'],
#                     help='output directory')
# 
# parser.add_argument('--num_img', type=int, nargs='?', default=setting['num_img'], help='number of images per row')
# parser.add_argument('--dpi', type=int, nargs='?', default=setting['dpi'], help='dpi controls the image resolution. For 4K/3840px, dpi is 240')
# 
# parser.add_argument('--overwrite', type=bool, nargs='?', default=setting['overwrite'], help='overwrite flag')
# 
# args = parser.parse_args()

# args = vars(args)

def local_plot():
    kwargs = load_setting()
    argv = sys.argv

    # patch to make it work when the args has __local__ inside it.
    if len(argv) > 1 and argv[1] == '__local__':
        del argv[1]

    if len(argv) >= 2:
        if argv[1] == 'combine_all_htmls':
            print(datetime.datetime.now())
            combine_all_htmls(kwargs['target_dir'])
            sys.exit()
        for fname in argv[1:]:
            if os.path.isfile(fname):
                convert_one_file(fname, **kwargs)
            elif os.path.isdir(fname):
                convert_folder(fname, **kwargs)
            else:
                print('fname is not a folder or dir')
    else:
        print('Usage: webplot fname.hdf     # plot one hdf file')
        print('Usage: webplot folder        # plot all hdf files in the folder')
        print('------------------------------------------------------------------')
        choice = input('press C to combine htmls or press S to setup the directory: ').lower().strip()
        if choice == 'c':
            combine_all_htmls(kwargs['target_dir'])
        elif choice == 's':
            generate_random_dir()
        elif choice == 't':
            test_plots()
        else:
            print(f'invalid input [{choice}]. quit')


if __name__ == '__main__':
    local_plot()
