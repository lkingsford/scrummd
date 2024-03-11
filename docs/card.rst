Cards
~~~~~

# Summary

A :ref:`card` is a markdown file with the ``.md`` extension which contains:

- A ``summary`` property
- An ``index`` - defined by the name of the card, or by an ```index`` field if provided

and may contain: 

- Single line property fields
- Multiple line permitted paragraph fields
- List fields
- Tags

To clarify, the ``index`` if there is no ``index`` field provided - the index of
the cards is the name of the file, ignoring the ``.md`` part of the name, and
ignoring any path.

So - a card in the file ``scrum/backlog/epic1/card1.md`` would have the index
``card1.md``. 

.. warning::
    An index **must** be unique to the repository. Preventing duplicate indexes
    is the responsibility of the team.


Example card
============

.. _cli017:

``cli017.md``
^^^^^^^^^^^^^

.. code-block:: markdown

    ---
    Summary: `sbl` relative file path output only
    Status: Done
    ---

    # Tags

    - Feature
    - Required for v1

    # Description

    We want to be able to just list the paths of all the cards that `sbl` returns when `sbl -b` or `sbl --bare` is called. The idea is that you'll be able to call

    ```
    vim `sbl scrum1`
    ```

    and be able to run the whole stand up going through the cards. Ordering the cards is a future goal.

    We want to add the `_path` field as well, so it can be used in other queries.

    # Depends

    - [[cli004]]

    # Cucumber

    **GIVEN** a collection of cards
    **WHEN** `sbl` is called with the `-b` or `--bare` parameter
    **THEN** the paths of all cards in the collection are returned with no other data - including no headers.

    **GIVEN** a column configuration including the `_path` field
    **WHEN** `sbl` is called
    **THEN** then the path of the card is shown

    # Implementation note

    No unit test exists for this actual output yet. I'm not really happy enough with output to test for it.


You'll note:

- It has a summary
- It has user defined Status, Description, Depends, Cucumber and Implementation note fields.
- It has a collection defined as the Depends - so, ``sbl cli017`` will return the card cli004.
- It has two tags defined - so, ``sbl Required`` and ``sbl "Required for v1""`` will return this card
- That Summary and Status are 'Property' style fields
- The the remainder of the fields are 'Paragraph' style fields and spread over multiple lines, divided by headers.

Fields
======

Special fields
--------------

The following fields have special meaning to ScrumMD.

``summary``
^^^^^^^^^^^

**Mandatory**

The summary of the card shown by default in ``sbl`` and other places.

``index``
^^^^^^^^^

The index of the card. This is used in preference over the index derived from
the name of the card.

.. _tags:
``tags`` or ``collections``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A list of collections to add the card to.

Paragraph Field Type
--------------------

A paragraph field type is defined as follows:

.. code-block:: markdown

    # FieldName

    Field value.

The field value extends until the next header. The header level is irrelevant -
``# todo`` and ``## todo`` will both create a field called ``todo``

.. note::
    Watch this space. I anticipate that this may change. I also expect that
    support for fields with lines underneath them becomes available in the
    future.

Property Field Type
-------------------

A set of property style fields is defined between pairs of `---`. Muliple
properties may be set at once. The properties should be set at the top of the
file.

They are defined as follows:

.. code-block:: markdown

    ---
    property1: value
    property2: value
    ---

Paragraph List Type
-------------------

Where a list must be defined (for instance, :ref:`tags`), a paragraph list
may be defined as follows:

.. code-block:: markdown

    # FieldName

    - List entry 1
    - List entry 2
     ...

Property List Type
------------------
Where a list must be defined (for instance, :ref:`tags`), a property list
may be defined as follows:

.. code-block:: markdown

    ---
    propertylist:
    - value
    - value
    ---

A property list can (and is expected) to be one of muliple properties between
``---`` markers.

Multiline Code blocks
---------------------

Multiline code blocks can be defined in markdown as between triple backticks -
as you can see in :ref:`cli017`.

ScrumMD ignores anything in a multiline code block.
