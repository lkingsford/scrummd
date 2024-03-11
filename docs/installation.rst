
Installation
============

Prerequisites
-------------

- Python 3.11+

Installing
----------

Globally
^^^^^^^^

On most platforms, you should be able to install ScrumMD for the current user
if you are not in a virtual environment by using ``pip``. ::

    pip install scrummd

Once ``pip`` has completed, ScrumMD should be ready to work. You can test it by
running ``sbl`` and seeing if it returns without an error.

Some platforms (Debian) do not permit ``pip`` to install outside of a virtual
environment without further changes.

In a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^

If you have already created and activated virtual environment,
``pip install scrummd`` will be sufficient to install ScrumMD. If not, to
create and activate a virtual environment:

macOS/Linux
"""""""""""

.. code-block:: text

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv env
    # . env/bin/activate

Windows
"""""""

.. code-block:: text

    > mkdir myproject
    > cd myproject
    > py -3 -m venv env
    > . env/scripts/activate

Once activated, ::

    pip install scrummd

will install ScrumMD to the virtual environment. You can test it by
running ``sbl`` and seeing if it returns without an error.
