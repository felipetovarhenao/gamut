# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from gamut.__version__ import __version__

sys.path.insert(0, os.path.abspath('../..'))

project = 'GAMuT'
copyright = '2023, Felipe Tovar-Henao'
author = 'Felipe Tovar-Henao'
version = f"v{__version__}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []
extensions = [
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
]
html_favicon = '_static/favicon.ico'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '../../gamut/gui/data/images/logo.png'
html_theme_options = {
    'logo_only': True,
    'display_version': True,
}
autodoc_typehints = "none"

pygments_style = 'monokai'
