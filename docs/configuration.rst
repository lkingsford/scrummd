.. _configuration:

Configuration
~~~~~~~~~~~~~

Configuration files
===================

ScrumMD is configured by a toml file. The first of the following files available
will be read for configuration:

-   ``.scrum.toml``
-   ``scrum.toml``
-   ``pyproject.toml``

All fields in the ``[tool.scrummd]`` collection.

Where fields are listed as ``[tool.scrummd.fieldname]``, they should be in
square brackets as TOML categories/arrays.

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




``required``
^^^^^^^^^^^^

Type
""""

array of str

Description
"""""""""""

List of fields that must be present in all cards.

``[tools.scrummd.fields.<field name>]``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type
""""

array of str

Description
"""""""""""

Limit *field name* to specific values. Each member is an array of str.

``[tools.scrummd.collections.<collection name>]``
#################################################

Additional restrictions which apply only to a specific collection.

``required``

Type
""""

array of str

Description
"""""""""""

List of fields that must be present in all cards in the collection.


``[tools.scrummd.collections.<collection name>.fields.<field name>]``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type
""""

array of str

Description
"""""""""""

Limit *field name* to specific values for all cards in the collection. Each
member is an array of str.

``[tools.scrummd.sbl]``
#######################

``columns``
^^^^^^^^^^^

Type
""""

array of string

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

``default_group_by``
^^^^^^^^^^^^^^^^^^^^

Type
""""

array of string

Description
"""""""""""

Default fields to group by if there's no ``--group-by`` field. Defaults to none.

``[tools.scrummd.sboard]``
##########################

``default_group_by``
^^^^^^^^^^^^^^^^^^^^

Type
""""

array of string

Description
"""""""""""

Default fields to group by if there's no ``--group-by`` field. 
A ``--group-by`` argument or ``default_group_by`` configuration must be set
for ``sboard`` to work.

``[tools.scrummd.scard]``
#########################

``reference_format``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Type
""""

str

Description
"""""""""""

Format of ``[[card]]`` fields when shown by ``scard``. Replaces ``$field`` with the field from the card.

Example configuration file
==========================

.. code-block:: toml

    [tool.scrummd]
    strict = true
    scrum_path = "scrum"
    omit_headers = false
    required = ["status"]

    [tool.scrummd.sbl]
    columns = ["index", "status", "summary"]
    # default_group_by is unset but commented as example
    # default_group_by = ["status"]

    [tool.scrummd.sboard]
    default_group_by = ["status"]
    
    [tool.scrummd.scard]
    reference_format = "$index [$status] ($assignee)"

    [tool.scrummd.fields]
    status = ["Not Fully Defined", "Ready", "In Progress", "In Testing", "Done"]

    [tool.scrummd.collections.epic]
    required = ["cost centre", "members"]

    [tool.scrummd.collections.epic.fields]
    cost_status = ["Not Costed", "Fully Costed"]
