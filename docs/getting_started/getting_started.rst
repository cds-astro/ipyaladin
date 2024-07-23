###############
Getting Started
###############

************
Installation
************

Released versions
~~~~~~~~~~~~~~~~~

To get the latest version of ``ipyaladin`` you can either use ``pip``,

.. code-block::

    pip install ipyaladin

or ``conda-forge``,

.. code-block::

    conda install ipyaladin -c conda-forge

and you're all set! 

Unreleased version
~~~~~~~~~~~~~~~~~~

To install the unreleased version, you will need npm, see its webpages for installation
instructions `https://www.npmjs.com/ <https://www.npmjs.com/>`_.

Then, download the ``ipyaladin`` github repository. From the root of the repository,
do 

.. code-block::

    npm run dev

You can then close the terminal with ``ctrl+c`` and the unreleased version of
 ``ipyaladin`` is installed on your machine.


****************
Using the widget
****************

You can open a notebook and instantiate an ``ipyaladin`` widget:

.. code-block:: python

    from ipyaladin import Aladin
    Aladin()

A widget should appear below this cell. See the ``getting started`` notebook example 
for a bit mot instantiation options, 

.. nbgallery::
    ../_collections/notebooks/01_Getting_Started

for a more detailed tour of ``ipyaladin``, have a look at the ``User Guide`` section.