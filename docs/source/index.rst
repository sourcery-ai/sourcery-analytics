.. sourcery-analytics documentation master file, created by
   sphinx-quickstart on Tue Apr 19 00:57:46 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ``sourcery-analytics``'s documentation!
==================================================

``sourcery-analytics`` is a library and command-line interface (CLI) for analyzing the code quality of Python
packages, modules, or source code.


Installation and Quickstart
===========================

Installation
------------

.. code-block::

   pip install sourcery_analytics

Analyze a file
--------------

.. code-block::

   sourcery-analytics analyze path/to/file.py


Contributing
============

Build this documentation
------------------------

.. code-block::

   sphinx-apidoc -eMTf --templatedir ./docs/source/_templates/apidoc -o docs/source/api sourcery_analytics
   sphinx-build -b html docs/source docs/build


Contents
========

.. toctree::
   :maxdepth: 3

   user_guide
   api/sourcery_analytics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
