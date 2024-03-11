.. _configuration:

Configuration
~~~~~~~~~~~~~

Configuration files
===================

.. note::
    It is intended that additional configuration will be able to be set on a per
    collection and per card basis. This is not implemented yet.

ScrumMD is configured by a toml file. The first of the following files available
will be read for configuration:

-   ``.scrum.toml``
-   ``scrum.toml``
-   ``pyproject.toml``

All fields in the ``[tool.scrummd]`` collection.

Supported fields
================

``[tool.scrummd]``
##################

``strict``
^^^^^^^^^^

Type
""""

bool

Description
""""""""""""

Fail on any issue with the collection rather than trying to persevere.


``scrum_path``
^^^^^^^^^^^^^^

Type
""""

string

Description
"""""""""""

Path to the Scrum repository containing cards and collections.

``columns``
^^^^^^^^^^^

Type
""""

string

Description
"""""""""""

Array of columns to show with ``sbl``.

``omit_headers``
^^^^^^^^^^^^^^^^

Type
""""

bool

Description
"""""""""""

Whether to omit headers from ``sbl`` output.


``scard_reference_format``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Type
""""

str

Description
"""""""""""

Format of ``[[card]]`` fields when shown by ``scard``. Replaces ``$field`` with the field from the card.

``[tools.scrummd.fields]``
##########################

*field name*
^^^^^^^^^^^^

Type
""""

array of str

Description
"""""""""""

Limit *field name* to specific values. Each member is an array of str.



Example configuration file
==========================

.. code-block:: toml

    [tool.scrummd]
    strict = true
    scrum_path = "scrum"
    columns = ["index", "status", "summary"]
    scard_reference_format = "$index [$status] ($assignee)"
    omit_headers = false

    [tool.scrummd.fields]
    status = ["Not Fully Defined", "Ready", "In Progress", "In Testing", "Done"]
