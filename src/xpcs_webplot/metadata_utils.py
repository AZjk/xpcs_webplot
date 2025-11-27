import os
import json
from pathlib import Path
import pandas as pd


from xpcs_webplot.plot_images import NpEncoder


def flatten_dict(d, parent_key="", sep="."):
    """
    Flatten a nested dictionary into a flat key-value structure.

    Recursively traverses a nested dictionary and converts it into a flat
    dictionary where nested keys are joined with a separator. Lists are
    converted to their string representation.

    Parameters
    ----------
    d : dict
        Dictionary to flatten. Can contain nested dictionaries and lists.
    parent_key : str, optional
        Prefix for keys (used in recursion). Default is ''.
    sep : str, optional
        Separator between nested keys. Default is '.'.

    Returns
    -------
    dict
        Dictionary with flattened keys. Nested keys are joined with the
        separator, and list values are converted to strings.

    Examples
    --------
    >>> nested = {'a': {'b': 1, 'c': 2}, 'd': [3, 4]}
    >>> flatten_dict(nested)
    {'a.b': 1, 'a.c': 2, 'd': '[3, 4]'}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to string representation
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def save_as_json(metadata, top_dir):
    """
    Save metadata dictionary as a JSON file.

    Creates a 'metadata' subdirectory in the specified top directory and
    saves the metadata as a formatted JSON file with 4-space indentation.
    Uses NpEncoder to handle NumPy data types.

    Parameters
    ----------
    metadata : dict
        Dictionary containing metadata to save. Can contain nested
        dictionaries and NumPy arrays.
    top_dir : str or Path
        Top-level directory where the metadata subdirectory will be created.

    Returns
    -------
    None

    Notes
    -----
    The output file will be saved at: `{top_dir}/metadata/metadata.json`

    See Also
    --------
    save_as_txt : Save metadata as a text file
    save_as_xlsx : Save metadata as an Excel file
    """
    save_name = Path(top_dir) / "metadata.json"
    save_name.parent.mkdir(parents=True, exist_ok=True)

    with open(save_name, "w") as f:
        json.dump(metadata, f, indent=4, cls=NpEncoder)


def convert_to_native_format(metadata):
    """
    Docstring for convert_to_native_format
    """
    metadata_native = json.loads(json.dumps(metadata, cls=NpEncoder))
    return metadata_native


def save_as_txt(metadata, top_dir):
    """
    Save metadata dictionary as a text file.

    Flattens the nested metadata dictionary and saves it as a text file
    with one key-value pair per line in the format "key: value".

    Parameters
    ----------
    metadata : dict
        Dictionary containing metadata to save. Nested dictionaries will
        be flattened with dot-separated keys.
    top_dir : str or Path
        Top-level directory where the metadata subdirectory will be created.

    Returns
    -------
    None

    Notes
    -----
    The output file will be saved at: `{top_dir}/metadata/metadata.txt`
    Nested dictionary keys are joined with '.' separator.

    See Also
    --------
    flatten_dict : Function used to flatten the nested dictionary
    save_as_json : Save metadata as a JSON file
    save_as_xlsx : Save metadata as an Excel file

    Examples
    --------
    For a metadata dict like {'a': {'b': 1}}, the output will be:
    a.b: 1
    """
    save_name = Path(top_dir) / "metadata.txt"
    save_name.parent.mkdir(parents=True, exist_ok=True)

    # Flatten the nested dictionary
    flat_metadata = flatten_dict(metadata)

    with open(save_name, "w") as f:
        for key, value in flat_metadata.items():
            f.write(f"{key}: {value}\n")


def save_as_xlsx(metadata, top_dir):
    """
    Save metadata dictionary as an Excel spreadsheet.

    Flattens the nested metadata dictionary and saves it as an Excel file
    with two columns: 'Key' and 'Value'.

    Parameters
    ----------
    metadata : dict
        Dictionary containing metadata to save. Nested dictionaries will
        be flattened with dot-separated keys.
    top_dir : str or Path
        Top-level directory where the metadata subdirectory will be created.

    Returns
    -------
    None

    Notes
    -----
    The output file will be saved at: `{top_dir}/metadata/metadata.xlsx`
    Nested dictionary keys are joined with '.' separator.
    Requires pandas with Excel writing support (openpyxl or xlsxwriter).

    See Also
    --------
    flatten_dict : Function used to flatten the nested dictionary
    save_as_json : Save metadata as a JSON file
    save_as_txt : Save metadata as a text file
    """
    save_name = Path(top_dir) / "metadata.xlsx"
    save_name.parent.mkdir(parents=True, exist_ok=True)

    # Flatten the nested dictionary
    flat_metadata = flatten_dict(metadata)

    df = pd.DataFrame(list(flat_metadata.items()), columns=["Key", "Value"])
    df.to_excel(save_name, index=False)


def save_metadata(metadata, top_dir):
    """
    Save metadata in multiple formats: JSON, text, and Excel.

    Calls individual functions to save the provided metadata dictionary
    in JSON, text, and Excel formats within a 'metadata' subdirectory
    of the specified top directory.

    Parameters
    ----------
    metadata : dict
        Dictionary containing metadata to save. Can contain nested
        dictionaries and NumPy arrays.
    top_dir : str or Path
        Top-level directory where the metadata subdirectory will be created.

    Returns
    -------
    None

    See Also
    --------
    save_as_json : Save metadata as a JSON file
    save_as_txt : Save metadata as a text file
    save_as_xlsx : Save metadata as an Excel file
    """
    meta_dir = Path(top_dir) / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    save_as_json(metadata, meta_dir)
    save_as_txt(metadata, meta_dir)
    save_as_xlsx(metadata, meta_dir)


def test():
    """
    Test function to demonstrate metadata saving functionality.

    Creates a sample metadata dictionary with XPCS experiment data and
    saves it in both text and Excel formats. This function serves as an
    example of how to use the metadata saving functions.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Notes
    -----
    The test saves files to a hardcoded directory path. Prints the paths
    of the saved files upon successful completion.

    The sample metadata includes:
    - Instrument configuration (attenuators, beam stop, detector, etc.)
    - XPCS analysis configuration
    - Sample information
    - User information

    See Also
    --------
    save_as_json : Save metadata as JSON
    save_as_txt : Save metadata as text
    save_as_xlsx : Save metadata as Excel
    """
    metadata = {
        "/entry/instrument": {
            "attenuator_1": {
                "attenuator_index": 12,
                "attenuator_transmission": 0.08666489644054544,
            },
            "attenuator_2": {"attenuator_index": 0, "attenuator_transmission": 0},
            "beam_stop": {
                "size": 4.0,
                "x_position": 103.835385,
                "y_position": 50.868170000000006,
            },
            "bluesky": {
                "bluesky_plan": "mesh_scan",
                "bluesky_plan_kwargs": "mesh_scan_sample_kwargs",
                "bluesky_version": "1.0.0",
                "parent_folder": "/gdata/dm/8ID/8IDI//2025-3/richards202511/data/",
                "scan_id": 1,
                "spec_file": "/gdata/dm/8ID/8IDI/2025-3/richards202511/data/richards202511.dat",
            },
            "datamanagement": {
                "workflow_kwargs": '{"qmap": "sample_name", "mask": "mask_name"}',
                "workflow_name": "xpcs8-boost-corr",
                "workflow_version": "0.0.1",
            },
            "detector_1": {
                "beam_center_position_x": -0.23,
                "beam_center_position_y": 0.17,
                "beam_center_x": 1676.0,
                "beam_center_y": 853.0,
                "compression": "bslz4",
                "count_time": 2e-05,
                "detector_name": "rigaku3M",
                "distance": 11.600022830000002,
                "flightpath_swing": 0.001338622999998762,
                "frame_time": 2e-05,
                "position_x": -0.22999996199999997,
                "position_y": 0.17000000499999998,
                "qmap_file": "rigaku3m_qmap_default.hdf",
                "rotation_x": 0.0,
                "rotation_y": 0.0,
                "rotation_z": 0.0,
                "x_pixel_size": 7.6e-05,
                "y_pixel_size": 7.6e-05,
            },
            "incident_beam": {
                "extent": 1e-06,
                "incident_beam_intensity": 1.1470708408355714e-06,
                "incident_energy": 12.184122959148514,
                "incident_energy_spread": 0.0001,
                "incident_polarization_type": "linear_horizontal",
                "ring_current": 0.0,
                "transmitted_beam_intensity": 0.0001,
            },
            "mono_slit": {
                "horizontal_center": 12.0,
                "horizontal_gap": 2.1,
                "vertical_center": 0.0,
                "vertical_gap": 3.85,
            },
            "monochromator": {
                "energy": 12.184122959148514,
                "wavelength": 0.9825905612216543,
            },
            "sl4": {
                "horizontal_center": 0.03669,
                "horizontal_gap": 0.10723,
                "vertical_center": 0.00805,
                "vertical_gap": 0.10941000000000001,
            },
            "sl7": {
                "horizontal_center": 0.02858,
                "horizontal_gap": 6.07988,
                "vertical_center": -0.030050000000000004,
                "vertical_gap": 6.081670000000001,
            },
            "undulator_1": {"energy": 1.0, "gap": 1.0, "taper": 1.0},
            "undulator_2": {"energy": 1.0, "gap": 1.0, "taper": 1.0},
            "wb_slit": {
                "horizontal_center": 16.75,
                "horizontal_gap": 0.53,
                "vertical_center": 2.25,
                "vertical_gap": 3.2,
            },
        },
        "/xpcs/multitau/config": {
            "analysis_type": "multitau",
            "avg_frame": 1,
            "begin_frame": 0,
            "end_frame": -1,
            "gpu_id": 2,
            "normalize_frame": True,
            "output": "/gdata/dm/8ID/8IDI/2025-3/richards202511/analysis/Multitau/",
            "overwrite": False,
            "qmap": "/gdata/dm/8ID/8IDI/2025-3/richards202511/data/rigaku3m_qmap_default.hdf",
            "raw": "/gdata/dm/8ID/8IDI/2025-3/richards202511/data/Ab0180_G10_a0011_f100000_r00001/Ab0180_G10_a0011_f100000_r00001.bin.000",
            "save_G2": False,
            "smooth": "sqmap",
            "stride_frame": 1,
            "verbose": True,
        },
        "/entry/sample": {
            "full_description": "Full sample description",
            "huber_chi": 89.9992994991,
            "huber_delta": 39.99968737360001,
            "huber_eta": -0.001104370800000004,
            "huber_mu": 0.0001374631640089774,
            "huber_nu": -0.00304588349996493,
            "huber_phi": 0.0017950797999999998,
            "huber_x": -0.0003900000000101045,
            "huber_y": 23.219685000000002,
            "huber_z": -0.0013550000000037699,
            "position_rheo_x": 0.0,
            "position_rheo_y": 0.0,
            "position_rheo_z": 0.0,
            "position_x": 299.22081329345707,
            "position_y": 20.810833435058594,
            "position_z": -0.01676483154296875,
            "qnw1_temperature": 20.0,
            "qnw1_temperature_set": 25.0,
            "qnw2_temperature": 20.0,
            "qnw2_temperature_set": 25.0,
            "qnw3_temperature": 20.0,
            "qnw3_temperature_set": 25.0,
            "qnw_lakeshore": 1.0,
            "rheometer_shear_rate": 1.0,
            "rheometer_temperature": 1.0,
            "short_description": "Short sample description",
        },
        "/entry/user": {
            "cycle": "2025-3",
            "email": "JohnDoe@mail.edu",
            "institution": "Institution Name",
            "name": "John Doe",
            "proposal_id": "none",
        },
        "analysis_type": ["Multitau"],
        "start_time": "2025-11-26 15:00:10.981503",
        "plot_time": "2025-11-26 15:40:30",
    }
    top_dir = "/home/beams/MQICHU/Datasets/xpcs/2025_1126_webplot_convertion/export"
    # save_as_json(metadata, top_dir)
    save_as_txt(metadata, top_dir)
    save_as_xlsx(metadata, top_dir)
    print("Files saved successfully!")
    print(f"TXT file: {Path(top_dir) / 'metadata' / 'metadata.txt'}")
    print(f"XLSX file: {Path(top_dir) / 'metadata' / 'metadata.xlsx'}")


if __name__ == "__main__":
    test()
