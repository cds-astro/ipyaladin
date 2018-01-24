ipyaladin
===============================

Description
-----------

A bridge between Jupyter and Aladin Lite, enabling interactive sky visualization in IPython notebooks.

![ipyaladin example](ipyaladin-screenshot.png)

With a couple of lines, you can display Aladin Lite, center it on the target of your choice, and overlay an Astropy table:

![ipyaladin example](ipyaladin-screencast.gif)

Examples
-----------

Some example notebooks can be found in the [examples directory](examples).

You can also try it directly [in mybinder](https://mybinder.org/v2/gh/cds-astro/ipyaladin/master?filepath=examples), without installing anything.

Installation
------------

To install use pip:

    $ pip install ipyaladin

Then, make sure to enable widgetsnbextension:

    $ jupyter nbextension enable --py widgetsnbextension
    
Finally, enable ipyaladin:

    $ jupyter nbextension enable --py --sys-prefix ipyaladin

There is also an experimental conda package that can be installed with:

    $  conda install -c tboch ipyaladin 


For a development installation (requires npm) you can either do:

    $ git clone https://github.com/cds-astro/ipyaladin
    $ cd ipyaladin
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipyaladin
    $ jupyter nbextension enable --py --sys-prefix ipyaladin

or directly use the compile.sh script:

    $ git clone https://github.com/cds-astro/ipyaladin
    $ cd ipyaladin
    $ ./compile.sh

Note:
Sometimes the module installation crash because of a conflict with an older occurence of itself, if so to solve this problem go to:  ~/anaconda3/share/jupyter/nbextensions
Then suppress the ipyaladin corrupted file.
