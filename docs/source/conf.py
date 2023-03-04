# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import codecs


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_logo():
    here = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(here), '../../gamut/gui/data/images/logo.png')


sys.path.insert(0, os.path.abspath('../..'))

project = 'GAMuT'
copyright = '2023, Felipe Tovar-Henao'
author = 'Felipe Tovar-Henao'
version = "v{}".format(get_version('../../gamut/__version__.py'))

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
html_logo = get_logo()
html_theme_options = {
    'logo_only': True,
    'display_version': True,
}
autodoc_typehints = "none"

pygments_style = 'monokai'
