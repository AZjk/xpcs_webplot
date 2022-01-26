import jinja2
import os


def convert_to_html(title, data_dict):
    outputfile = title + '.html'

    subs = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template.html').render(title=title, mydata=data_dict)

    # lets write the substitution to a file
    with open(outputfile, 'w') as f:
        f.write(subs)


def combine_all_htmls(target_folder='result'):
    files = os.listdir(target_folder)
    htmls = [x for x in files if x.endswith('.html')]
    htmls.sort()
    htmls_dict = {}

    for x in htmls:
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

