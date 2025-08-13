==========================
XPCS-WEBPLOT Quick Guide
==========================

:Author: Miaoqi Chu
:Email: mqichu@anl.gov

Architecture Overview
=====================

**Data Types**

- Multitau results
- Twotime results  
- Raw data

**Workflow**

- ``boost_corr`` with DM → ``webplot plot`` → Multitau/Two-time HTML → Indexed webpage
- Hosted via HTTP server using ``webplot serve``

Step 1: Setup the Host Machine
===============================

**Machine Requirements:**

- Must access processed results (e.g., ``/gdata``)
- Suggested: ``adamite`` (high RAM & CPU)
- Login: ``ssh 8idiuser@adamite``

**Manage tmux Session:**

- Check: ``tmux ls``
- Attach: ``tmux a -t webplot``
- Or create new::

    tmux
    # Rename: CTRL + b, then type
    :rename-session webplot

**Activate Environment:**

.. code-block:: bash

   conda activate /home/beams/MQICHU/.conda/envs/p2504_xpcs

.. note::
   Ask beamline staff for the latest version.

Step 2: Monitor and Convert Results to HTML
============================================

.. code-block:: bash

   xpcs_webplot plot /path/to/results --monitor --target-dir /path/to/htmls --num-workers 4

- Replace ``/path/to/...`` with actual directories.
- ``htmls`` folder must be accessible by public machines, e.g.:

  - ``/home/8-id-i/2025-1/xxx``
  - ``/home/8-id-e/2025-1/xxx``

xpcs_webplot plot – Full CLI Reference
=======================================

.. code-block:: bash

   xpcs_webplot plot [-h] [--target-dir TARGET_DIR]
                     [--image-only] [--num-img NUM_IMG]
                     [--dpi DPI] [--overwrite]
                     [--monitor] [--num-workers NUM_WORKERS]
                     [--max-running-time MAX_RUNNING_TIME]
                     fname

**Arguments:**

- ``fname``: input HDF5 file or result folder (required)

**Options:**

- ``--target-dir TARGET_DIR``: output directory (default: ``/tmp``)
- ``--image-only``: only generate images, no HTML
- ``--num-img NUM_IMG``: number of images per row (default: 4)
- ``--dpi DPI``: image resolution - controls DPI for output images (default: 240). For 4K monitors, DPI can be set to 240 to produce images with 3840 horizontal pixels
- ``--overwrite``: overwrite existing files
- ``--monitor``: watch folder for new files and process them automatically
- ``--num-workers NUM_WORKERS``: number of worker processes for parallel processing (default: 8)
- ``--max-running-time MAX_RUNNING_TIME``: maximum running time in seconds (default: 604800, which is 7 days)

Step 3: Host HTML with HTTP Server
===================================

**Suggested machine:** ``kouga`` (must access HTML output folder and must be visible to the machines with public IPs)

**Use tmux:**

- Check: ``tmux ls``
- Attach: ``tmux a -t webplot-serve``
- Or create new and rename::

    tmux
    # Rename: CTRL + b, then type
    :rename-session webplot-serve

**Activate the same conda environment**

xpcs_webplot serve – Full CLI Reference
========================================

.. code-block:: bash

   xpcs_webplot serve [-h] [--target-dir TARGET_DIR] [--port PORT]

**Options:**

- ``--target-dir TARGET_DIR``: the plot directory to host the server (default: current directory ``.``)
- ``--port PORT``: port to run the HTTP server (default: 8081)

The server will display both local and network URLs for access:

- Local: ``http://localhost:PORT``
- Network: ``http://LOCAL_IP:PORT``

Additional Commands
===================

xpcs_webplot combine
---------------------

Combine multiple HTML files into a single indexed webpage.

.. code-block:: bash

   xpcs_webplot combine [-h] [target_dir]

**Arguments:**

- ``target_dir``: the plot directory containing HTML files to combine (optional)

Usage Examples
==============

**Process a single HDF5 file:**

.. code-block:: bash

   xpcs_webplot plot /path/to/result.hdf --target-dir /output/dir

**Monitor a directory for new files:**

.. code-block:: bash

   xpcs_webplot plot /path/to/results --monitor --target-dir /output/dir --num-workers 8

**Generate high-resolution images only:**

.. code-block:: bash

   xpcs_webplot plot /path/to/result.hdf --image-only --dpi 300

**Serve HTML files on a custom port:**

.. code-block:: bash

   xpcs_webplot serve --target-dir /path/to/htmls --port 8080

**Combine existing HTML files:**

.. code-block:: bash

   xpcs_webplot combine /path/to/htmls
