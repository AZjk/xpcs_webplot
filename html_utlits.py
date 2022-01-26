import jinja2
import os
import json


def convert_to_html(save_dir, data_dict):
    outputfile = save_dir + '.html'
    title = os.path.basename(save_dir)

    subs = jinja2.Environment(loader=jinja2.FileSystemLoader(
        './')).get_template('template_single.html').render(title=title, mydata=data_dict)

    # lets write the substitution to a file
    with open(outputfile, 'w') as f:
        f.write(subs)


def combine_all_htmls(fname='index.html', target_folder='html'):
    files = os.listdir(target_folder)
    htmls = [x for x in files if x.endswith('.html')]
    if 'index.html' in htmls:
        htmls.remove('index.html')
    htmls.sort()

    html_info = []
    for x in htmls:
        short_label = os.path.splitext(x)[0]
        json_fname = os.path.join(target_folder, short_label, 'metadata.json') 
        with open(json_fname, 'r') as f:
            meta = json.load(f)
        html_info.append([
            short_label, x, meta['analysis_type'], meta['t_begin']
        ])
    subs = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template_combined.html').render(mydata=html_info)
    # lets write the substitution to a file
    with open(os.path.join(target_folder, fname), 'w') as f:
        f.write(subs)


if __name__ == '__main__':
    combine_all_htmls()
