# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
import typing

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "sourcery-analytics"
copyright = "2022, Sourcery.ai"
author = "Ben Martineau"
html_baseurl = "https://sourcery-analytics.sourcery.ai/"  # CNAME


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",  # Handle google-style docstrings
    "sphinx.ext.autodoc",  # Read docstrings and modules
    "sphinx.ext.intersphinx",  # Cross-references to other documentation
    "sphinx.ext.doctest",  # inline doctest snippets
    "sphinx.ext.githubpages",  # CNAME and .nojekyll
    "sphinx_copybutton",  # copyable code
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: typing.List[str] = []


# -- Options for HTML output -------------------------------------------------


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# Intersphinx config
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.9", None),
    "astroid": ("https://pylint.pycqa.org/projects/astroid/en/latest/", None),
}

# Autodoc Typehints config
autodoc_typehints = "signature"
autodoc_class_signature = "mixed"
autodoc_typehints_format = "short"
autodoc_unqualified_typehints = True
autodoc_preserve_defaults = True
autodoc_member_order = "bysource"
autodoc_type_aliases = {
    "Metric": "sourcery_analytics.metrics.Metric",
}


# Sphinx Material
html_theme = "sphinx_material"  # custom theme
html_logo = "_static/img/sourcery-logo-300-greyscale.png"
html_theme_options = {
    "nav_title": "Sourcery Analytics",
    "repo_url": "https://github.com/sourcery-ai/sourcery-analytics",
    "repo_name": "sourcery-ai/sourcery-analytics",
    "repo_type": "github",
    "globaltoc_depth": 3,
}
html_title = "Sourcery Analytics"
html_short_title = "Sourcery Analytics"
html_sidebars = {"**": ["globaltoc.html", "localtoc.html", "searchbox.html"]}


# sphinx_copybutton config
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
