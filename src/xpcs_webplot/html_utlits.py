import jinja2
import os
import json
import shutil
import sys
import logging
import glob


logger = logging.getLogger(__name__)


template_path = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(template_path, "templates")


def copy_minipreview(target_folder):
    """
    Copy minipreview JavaScript and CSS files to target folder.

    Copies the jQuery minipreview plugin files required for HTML preview
    functionality to the specified target folder.

    Parameters
    ----------
    target_folder : str
        Destination folder where minipreview files will be copied.

    Returns
    -------
    None

    Notes
    -----
    Copies the following files:
    - jquery.minipreview.css
    - jquery.minipreview.js
    
    Files are only copied if they don't already exist in the target folder.

    See Also
    --------
    combine_all_htmls : Uses this function to prepare combined HTML pages
    """
    source_dir = os.path.join(template_path, "mini-preview/")
    flist = ["jquery.minipreview.css", "jquery.minipreview.js"]
    for f in flist:
        target_file = os.path.join(target_folder, f)
        if not os.path.isfile(f):
            shutil.copy(os.path.join(source_dir, f), target_file)
    return


def convert_to_html(save_dir, data_dict):
    """
    Generate HTML summary page from XPCS analysis data.

    Creates an HTML file using a Jinja2 template to display XPCS analysis
    results including plots and metadata.

    Parameters
    ----------
    save_dir : Path or str
        Directory where the summary.html file will be saved.
    data_dict : dict
        Dictionary containing data to render in the HTML template.
        Expected keys include:
        - 'scattering' : path to SAXS scattering plot
        - 'stability' : path to stability plot
        - 'correlation' : list of correlation function plot paths
        - 'metadata' : dictionary of analysis metadata

    Returns
    -------
    None

    Notes
    -----
    The output file is saved as 'summary.html' in the save_dir directory.
    Uses the 'single.html' Jinja2 template.

    See Also
    --------
    convert_single_folder : Prepare data dictionary and call this function
    plot_xpcs_result : Generate plots and call this function
    """
    # outputfile = save_dir.with_suffix(".html")
    outputfile = save_dir / "summary.html"
    title = os.path.basename(save_dir)

    loader = jinja2.FileSystemLoader(template_path)
    subs = (
        jinja2.Environment(loader=loader)
        .get_template("single.html")
        .render(title=title, mydata=data_dict)
    )

    # lets write the substitution to a file
    with open(outputfile, "w") as f:
        f.write(subs)


def convert_single_folder(target_folder):
    """
    Convert a single result folder to HTML format.

    Processes a folder containing XPCS analysis results (plots and metadata)
    and generates an HTML summary page.

    Parameters
    ----------
    target_folder : str
        Path to the folder containing analysis results. The folder should
        contain PNG plot files and a metadata.json file.

    Returns
    -------
    None

    Notes
    -----
    Expected folder contents:
    - saxs_mask.png : SAXS scattering pattern with mask
    - stability.png : Stability analysis plot
    - *.png : Additional correlation function plots
    - metadata.json : Analysis metadata
    
    The function generates a summary.html file in the target folder.

    See Also
    --------
    convert_to_html : Generate HTML from data dictionary
    combine_all_htmls : Combine multiple HTML results
    """
    realpah = os.path.realpath(target_folder)
    save_dir = realpah.rstrip()
    basename = os.path.basename(realpah)
    files = os.listdir(realpah)
    files = [os.path.join(basename, x) for x in files if x.endswith(".png")]
    html_dict = {
        "scattering": os.path.join(basename, "saxs_mask.png"),
        "stability": os.path.join(basename, "stability.png"),
    }
    files.remove(html_dict["scattering"])
    files.remove(html_dict["stability"])
    files.sort()
    html_dict["correlation"] = files
    with open(os.path.join(realpah, "metadata.json"), "r") as f:
        html_dict["metadata"] = json.load(f)
    convert_to_html(save_dir, html_dict)
    return


def combine_all_htmls(html_dir="html"):
    """
    Combine multiple XPCS result HTMLs into a single index page.

    Scans a folder containing multiple XPCS analysis results and generates
    combined index pages for easy navigation and browsing.

    Parameters
    ----------
    html_dir : str, optional
        Path to the folder containing HTML result subdirectories.
        Default is "html".

    Returns
    -------
    None

    Notes
    -----
    The function:
    1. Scans for HTML files in the html_dir
    2. Extracts metadata from each result's metadata.json
    3. Generates combined index pages:
       - index.html
       - preview.html
       - iframe.html
    4. Copies minipreview JavaScript/CSS files
    5. Sorts results by start time (most recent first)
    
    Each result entry includes:
    - Short name (derived from filename)
    - Analysis type
    - Start time
    - Plot generation time

    See Also
    --------
    convert_to_html : Generate individual HTML summaries
    copy_minipreview : Copy required JavaScript/CSS files

    Examples
    --------
    >>> combine_all_htmls('output')
    INFO: hdf files combined: [output]
    INFO: --total number of files: [42]
    """
    targets = ["index.html", "preview.html", "iframe.html"]
    htmls = glob.glob(os.path.join(html_dir, "*/summary.html"), recursive=True)
    htmls.sort()

    html_info = []
    for x in htmls:
        short_label = os.path.basename(os.path.dirname(x))
        short_name = short_label.rstrip("_results")
        json_fname = os.path.join(os.path.dirname(x), "metadata", "metadata.json")
        try:
            with open(json_fname, "r") as f:
                meta = json.load(f)
                v1, v2, v3 = (
                    meta["analysis_type"],
                    meta["start_time"],
                    meta["plot_time"],
                )
        except Exception as e:
            logger.error(str(e))
        else:
            relative_path = os.path.join(*x.split(os.sep)[-2:])
            html_info.append([short_name, relative_path, v1, v2, v3])
    html_info.sort(key=lambda x: x[3], reverse=True)
    tfiles = ["combined.html", "combined_preview.html", "combined_iframe.html"]

    loader = jinja2.FileSystemLoader(template_path)
    for target, template in zip(targets, tfiles):
        subs = (
            jinja2.Environment(loader=loader)
            .get_template(template)
            .render(mydata=html_info)
        )
        # lets write the substitution to a file
        static_html_path = os.path.join(html_dir, "static_" + target) 
        with open(static_html_path, "w") as f:
            f.write(subs)

    copy_minipreview(html_dir)
    logger.info(f"hdf files combined: [{html_dir}]")
    logger.info(f"--total number of files: [{len(html_info)}]")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        combine_all_htmls(sys.argv[1])
    # convert_single_folder(sys.argv[1])
