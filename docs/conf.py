# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import tomllib
from pathlib import Path

with Path.open("../pyproject.toml", "rb") as config:
    toml = tomllib.load(config)
import datetime
from ipyaladin import __version__, Aladin

project = toml["project"]["name"]
author = "Strasbourg Astronomical Date Centre (CDS)"
copyright = f"{datetime.datetime.now().year}, {author}"  # noqa: A001
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# By default, highlight as Python 3.
highlight_language = "python3"

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxcontrib.collections",
    # To support Numpy docstrings, we use this extension:
    "numpydoc",
    "nbsphinx",
    "sphinx_copybutton",
    "sphinx_gallery.load_style",
    "autoapi.extension",
    "myst_parser",
]

jupyterlite_config = "jupyterlite_config.json"

autoapi_dirs = ["../src"]
autoapi_options = ["members", "show-module-summary"]


intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "astropy": ("http://docs.astropy.org/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "regions": ("https://astropy-regions.readthedocs.io/en/stable", None),
}

source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# -- Add the notebooks to Sphinx root folder with collections ----------------

collections = {
    "notebooks": {
        "driver": "copy_folder",
        "source": "../examples/",
        "target": "notebooks",
        "ignore": [".ipynb_checkpoints/*"],
    }
}

# this allows to set thumbnails for the notebooks
notebooks = Path().glob("../examples/*.ipynb")
notebooks = [
    str(notebook).split("/")[-1].replace(".ipynb", "") for notebook in notebooks
]
thumbnail_path = "_static/notebooks_thumbnails/"
collections_path = "_collections/notebooks/"
nbsphinx_thumbnails = {
    f"{collections_path}{notebook}": f"{thumbnail_path}{notebook.split('_')[0]}.png"
    for notebook in notebooks
}

# -- Document Init Options ---------------------------------------------------

init_options = Aladin().traits(only_init=True)

with Path.open("user_documentation/init_options.csv", "w"):
    pass  # flush the file

with Path.open("user_documentation/init_options.csv", "a") as f:
    for k, v in init_options.items():
        f.write(f"{k};{v.default_value};{v.help}\n")


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

language = "en"

html_static_path = ["_static"]

html_theme = "pydata_sphinx_theme"
html_favicon = "_static/aladin-logo.svg"

html_theme_options = {
    "show_nav_level": 2,
    "show_toc_level": 3,
    "content_footer_items": ["last-updated"],
    "github_url": "https://github.com/cds-astro/ipyaladin",
    "external_links": [
        {"name": "Aladin", "url": "https://aladin.cds.unistra.fr/aladin.gml"},
        {
            "name": "Changelog",
            "url": "<https://github.com/cds-astro/ipyaladin/releases>",
        },
    ],
    "logo": {
        "alt-text": "Ipyaladin documentation - Home",
        "text": "Ipyaladin documentation",
        "image_light": "_static/ipyaladin_light.png",
        "image_dark": "_static/ipyaladin_dark.png",
    },
    "back_to_top_button": True,
    "pygments_dark_style": "lightbulb",  # chose from higher contrasts for accessibility
    "pygments_light_style": "default",
}
