
Concepts
--------

Before we get started, it'd be helpful to understand the basic ideas of using
ScrumMD.

.. _repository: 

Repository
^^^^^^^^^^

A **Repository** is the folder containing all of the cards for a project. By
default, ScrumMD expects that the repository is located in a folder called
`scrum` - but this can be configured to be different.


.. _card: 

Card
^^^^

A **Card** is a file in markdown format. It is given an index (card number) of
its filename unless otherwise overwritten by an index field.

It must contain at minimum a 'Summary' field. An example card might look like:

.. _tool01.md:

``backlog/tool01.md``
"""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Create entry point
    status: Ready for development
    ---

    # Description

    Create an entry point for `tool` so it can be accessed by the command line.

    # Dependencies

    - [[tool02]]
    - [[tool03]]

.. _field:

Field
^^^^^

A **Field** is any text in a markdown file that is in a property block (like
``summary`` in :ref:`tool01.md` above) or under a heading (like ``description``
and ```dependencies`` in :ref:`tool01.md` above) can be treated as a field.

.. _collection: 

Collection
^^^^^^^^^^

A **Collection** is a group of cards. Collections can be made in three ways:

- A subfolder that a card is in is a Collection.
- Any cards referred to in a Field become a collection.
- A Field called ``tags`` or ``collections`` will add a card to the collections listed in it.

In :ref:`tool01.md` above, ``tool01`` will be in the ``backlog`` collection 
(because of its file path) and it will define the ``tool01.dependencies``
collection that will include ``tool02`` and ``tool03``.

A folder inside a folder becomes a **sub-collection** - so, if you had a
``backlog`` folder and inside that, a ``epics`` folder, then any cards inside
the ``epics`` folder would be in both the ``backlog`` and ``backlog.epics``
collections.

A card may be in multiple collections.

Collection sorting
^^^^^^^^^^^^^^^^^^

``sbl`` provides ``sort-by`` as an argument to allow you to sort cards, but - if
you define a collection with the cards referenced in a card, they'll maintain
the same order. 

Given Scrum treats the order of cards in the Backlog and Sprint as important,
you might choose to have your cards in a ``stories`` or ``features`` folder,
and then intentionally create a backlog - for instance:

``backlog.md``

.. code-block:: markdown

    ---
    Summary: Backlog
    ---

    # Items

    - [[card1]]
    - [[card5]]
    - [[card12]]
    - [[card2]]
