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

   $ pip install sourcery_analytics

Analyze a file
--------------

.. code-block::

   $ sourcery-analytics analyze path/to/file.py

Example
-------

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/analysis.py

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
   ┃ Method                                      ┃ length ┃ cyclomatic_complexity ┃ cognitive_complexity ┃ working_memory ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
   │ sourcery_analytics.analysis.analyze         │      5 │                     1 │                    0 │              8 │
   │ sourcery_analytics.analysis.analyze_methods │      4 │                     1 │                    1 │             12 │
   └─────────────────────────────────────────────┴────────┴───────────────────────┴──────────────────────┴────────────────┘



Contents
========

.. toctree::
   :maxdepth: 3

   user_guide
   metrics
   developer_guide
   api/sourcery_analytics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
