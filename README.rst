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




Python Boilerplate contains all the boilerplate you need to create a Python package.


* Free software: MIT license
* Documentation: https://xpcs-webplot.readthedocs.io.


Start Nginx web server
-------

* login axinite as 8idiuer
    ``ssh 8idiuser@axinite.xray.aps.anl.gov -Y``

* check if Nginx is running
     ``docker container ls | grep nginx``

* stop Nginx if you want to switch to a new html folder
     ``docker stop webplothttp``
 
* start a new Nginx server, replace CYCLE with the correct values,
    ``docker run --rm --name webplothttp -v /net/wolf/data/xpcs8/CYCLE/html:/usr/share/nginx/html:ro -p 80:80 -d nginx``
    


Run webplot in the background
-------

* login axinite as 8idiuer
    ``ssh 8idiuser@axinite.xray.aps.anl.gov -Y``

* resume the screen session for webplot
    ``screen -xS webplot``
    
    if you see messages like ``There is no screen to be attached matching webplot.``, then start a new session
    ``screen -S webplot``

* switch to the 1st panel of the screen session, press ``CTRL + A``, then press ``1``

* run webplot if it's not running
    ``watch -n 120 webplot combine_all_htmls``

    this will run the command ``webplot combine_all_htmls`` every ``120`` seconds.

* exit screen by press ``CTRL + A``, then press ``d``. Now you are safe to terminate the ssh session. webplot will be running in the background.
       

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
