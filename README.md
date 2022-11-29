# ipyaladin

## Description

A bridge between Jupyter and Aladin Lite, enabling interactive sky visualization in IPython notebooks.

![ipyaladin example](ipyaladin-screenshot.png)

With a couple of lines, you can display Aladin Lite, center it on the target of your choice, and overlay an Astropy table:

![ipyaladin example](ipyaladin-screencast.gif)

## Examples

Some example notebooks can be found in the [examples directory](examples).

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/bmatthieu3/ipyaladin/fix-model-aladin). You can also try it directly [in mybinder](https://mybinder.org/v2/gh/bmatthieu3/ipyaladin/fix-model-aladin), without installing anything.

## Installation

To install use pip:

    $ pip install ipyaladin

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/cds-astro/ipyaladin.git
    $ cd ipyaladin
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix ipyaladin
    $ jupyter nbextension enable --py --sys-prefix ipyaladin

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite ipyaladin

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
