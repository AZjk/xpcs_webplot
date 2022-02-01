import jinja2
import os
import json
import shutil
import sys


def copy_minipreview(target_folder):
    source_dir = "template/mini-preview/"
    flist = ['jquery.minipreview.css', 'jquery.minipreview.js']
    for f in flist:
        target_file = os.path.join(target_folder, f)
        if not os.path.isfile(f):
            shutil.copy(os.path.join(source_dir, f), target_file)
    return


def convert_to_html(save_dir, data_dict):
    outputfile = save_dir + '.html'
    title = os.path.basename(save_dir)

    subs = jinja2.Environment(loader=jinja2.FileSystemLoader(
        './')).get_template('template/single.html').render(title=title, mydata=data_dict)

    # lets write the substitution to a file
    with open(outputfile, 'w') as f:
        f.write(subs)


def combine_all_htmls(target_folder='html'): 
    targets = ['index.html', 'preview.html']
    files = os.listdir(target_folder)
    htmls = [x for x in files if x.endswith('.html')]
    htmls.sort()

    html_info = []
    for x in htmls:
        if x in targets:
            continue
        short_label = os.path.splitext(x)[0]
        json_fname = os.path.join(target_folder, short_label, 'metadata.json') 
        try:
            with open(json_fname, 'r') as f:
                meta = json.load(f)
                v1, v2 = meta['analysis_type'], meta['t_begin']
        except Exception:
            pass
        else:
            html_info.append([
                short_label, x, v1, v2
            ])

    tfiles = ['template/combined.html', 'template/combined_preview.html']

    for target, template in zip(targets, tfiles):
        subs = jinja2.Environment(
            loader=jinja2.FileSystemLoader('./')
        ).get_template(template).render(mydata=html_info)
        # lets write the substitution to a file
        with open(os.path.join(target_folder, target), 'w') as f:
            f.write(subs)

    copy_minipreview(target_folder)
    basename = os.path.basename(target_folder)
    print(f'hdf files combined: [{target_folder}]')
    print(f'--total number of files: [{len(html_info)}]')
    print(f'--open link http://164.54.100.176/{basename}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        combine_all_htmls(sys.argv[1])
