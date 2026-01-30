============
xpcs_webplot
============


.. image:: https://img.shields.io/pypi/v/xpcs_webplot.svg
        :target: https://pypi.python.org/pypi/xpcs_webplot

.. image:: https://img.shields.io/travis/AZjk/xpcs_webplot.svg
        :target: https://travis-ci.com/AZjk/xpcs_webplot

.. image:: https://readthedocs.org/projects/xpcs-webplot/badge/?version=latest
        :target: https://xpcs-webplot.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




XPCS WebPlot is a Python package for converting X-ray Photon Correlation Spectroscopy (XPCS) analysis results into interactive web-viewable formats.

Features
--------

* Convert XPCS HDF5 files to HTML with plots and data exports
* Flask-based web server for browsing results with split-view layout
* Batch processing with parallel execution
* Real-time directory monitoring for automatic processing
* Flexible output options and customization

* Free software: MIT license
* Documentation: https://xpcs-webplot.readthedocs.io.

Quick Start
-----------

Installation::

    pip install -e .

Convert a single file::

    xpcs_webplot plot input.hdf --html-dir ./html

Start web server::

    xpcs_webplot serve ./html

Documentation
-------------

Comprehensive documentation is available in the ``docs/`` directory:

* `Getting Started <docs/getting_started.md>`_ - Installation and basic usage
* `User Guide <docs/user_guide.md>`_ - Complete command reference
* `API Reference <docs/api_reference.md>`_ - Programmatic usage
* `Quick Reference <docs/quick_reference.md>`_ - Command cheat sheet
* `Architecture <docs/architecture.md>`_ - System design
* `Development Guide <docs/development_guide.md>`_ - Contributing
* `Deployment Guide <docs/deployment_guide.md>`_ - Production setup
* `FAQ <docs/faq.md>`_ - Troubleshooting and common questions
