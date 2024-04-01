
Tutorial: Basics of using ScrumMD
------------------------------------------------

.. note::

    This tutorial assumes basic skills in your respective command line shell,
    and that scrummd is either set up globally or in the activate virtual
    environment.


Creating the repository
^^^^^^^^^^^^^^^^^^^^^^^

Firstly, we've got to create a :ref:`repository`. All that the repository is
is a folder that contains your cards. If you're using ScrumMD to manage a
software project, you might choose to keep your repository in the same Git
repository as your code, or you might choose to keep them completely separate,

ScrumMD looks for a ``scrum`` folder by default. Navigate to where you want to
create the repository and then:

macOS/Linux
"""""""""""

.. code-block:: text

    $ mkdir scrum

Windows
"""""""

.. code-block:: text

    > mkdir scrum


Creating a card
^^^^^^^^^^^^^^^

A :ref:`card` doesn't need to be in a :ref:`collection`, but lets create one anyway. You're
probably going to want one to keep track of them. In Scrum, it's common to
keep all of your cards in backlog, so lets create the backlog folder.

macOS/Linux
"""""""""""

.. code-block:: text

    $ mkdir scrum/backlog

Windows
"""""""

.. code-block:: text

    > mkdir scrum\backlog

Open ``scrum/backlog/card1.md`` in your preferred text editor and add and save
the following:

``scrum/backlog/card1.md``
"""""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: My first Scrum card
    ---

We're also going to create a second collection, and add a card to it. 

macOS/Linux
"""""""""""

.. code-block:: text

    $ mkdir scrum/reports

Windows
"""""""

.. code-block:: text

    > mkdir scrum\reports

Open ``scrum/reports/bug.md`` in your preferred text editor and add and save
the following:

``scrum/reports/bug1.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bug with project
    reporter: example@example.com
    ---

    # Description  

    Demonstrate another collection of cards


Viewing the collections
^^^^^^^^^^^^^^^^^^^^^^^

Now, if from our root directory, we call ``sbl``, we'll get a listing of all of
the Scrum cards:

.. code-block:: text

    $ sbl
    index, summary
    card1, My first Scrum card
    bug1, Bug with project

If we wanted just the items in a specific collection, we can call
``sbl [collection_name`` - so:

.. code-block:: text

    $ sbl backlog
    index, summary
    card1, My first Scrum card

Modifying ``sbl`` output
^^^^^^^^^^^^^^^^^^^^^^^^

If you type ``sbl --help``, you'll see there are a few ways to modify the
output without even using a configuration file.

We're going to try customizing the fields being shown, and use grouping.  
Open the following files in your text editor and modify/create them as listed:
following:

``scrum/reports/bug1.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bug with project
    reporter: example@example.com
    severity: High
    ---

    # Description  

    Demonstrate another collection of cards


``scrum/reports/bug2.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bug with project 2
    reporter: example@example.com
    severity: Low
    ---

    # Description  

    Nobody cares about this bug


``scrum/reports/bug3.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bad bug
    reporter: example2@example.com
    severity: High
    ---

    # Description  

    But they care about this one.

If we call ``sbl reports`` - we'll still get something useful:

.. code-block:: text

    $ sbl reports
    index, summary
    bug3, Bad bug
    bug2, Bug with project 2
    bug1, Bug with project

But - we could group by the Severity by using ``--group-by severity`` and add
the output of the reporter with a ``-c`` command as follows:

.. code-block:: text

    sbl reports --group-by severity --columns index,summary,reporter
    index, summary, reporter
    [severity = high]
    bug3, Bad bug, example2@example.com
    bug1, Bug with project, example@example.com
    [severity = low]
    bug2, Bug with project 2, example@example.com
    [severity = None]


``bare`` mode
^^^^^^^^^^^^^

Using ``sbl -b`` can give a list of relative paths in the collection and nothing
more:

.. code-block:: text

    $ sbl reports -b
    scrum/reports/bug3.md
    scrum/reports/bug2.md
    scrum/reports/bug1.md

If you're using ``bash`` or similar as your shell, you are then able to call
``sbl -b`` in backticks as the parameter to a text-editor to load all the
cards at once. For instance - if you were refining the bug reports, you could
use ``vim `sbl reports -b` `` to load all the bug reports in vim.


Viewing cards
^^^^^^^^^^^^^

ScrumMD comes with ``scard`` which will give you a full output of the referenced
cards:

.. code-block:: text

    # sbl bug1 bug2 bug3
    ---
    bug1: Bug with project
    ---
    reporter: example@example.com
    severity: High
    description: 
    Demonstrate another collection of cards

    ---
    bug2: Bug with project 2
    ---
    reporter: example@example.com
    severity: Low
    description: 
    Nobody cares about this bug

    ---
    bug3: Bad bug
    ---
    reporter: example2@example.com
    severity: High
    description: 
    But they care about this one.


Configuration
^^^^^^^^^^^^^

Configuration is in ``toml`` files. ScrumMD looks for configuration in the
following files (in this order):

- ``.scrum.toml``
- ``scrum.toml``
- ``pyproject.toml``

See :ref:`configuration` for more details.

We're going to use the configuration to limit the allowed values of
``severity``. Create the following file in the same directory that contains
``scrum``.

scrum.toml
""""""""""

..text-block:: toml

    [tool.scrummd]
    strict = true

    [tool.scrummd.fields]
    severity = ["High", "Medium", "Low"]

This set some permitted values for ``severity``, and enabled strict mode: 
meaning that if there are any errors, the programs will refuse to run.

Now, create the following file:

``scrum/reports/bug4.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bad bug
    reporter: example2@example.com
    severity: Bad
    ---

If we run ``sbl reports``, we'll see an error:

.. code-block:: text

    $ sbl reports
    ERROR:root:ValidationError (severity is "Bad". Per configuration, severity must be one of [High, Medium, Low]) reading scrum/reports/bug4.md

Delete ``bug4.md`` before continuing on the tutorial.

References
^^^^^^^^^^

You can add references to a card by referring to its index/card number in
double-square brackets - like ``[[bug01]]``.

By default - ``scard`` will replace it with a reference to the index and the
summary - but, this can be configured to include another field. For instance,
you might use the configuration to include the ``status`` field of the card.

Firstly, we'll modify the following file to add a reference:

``scrum/reports/bug1.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bug with project
    reporter: example@example.com
    severity: High
    ---

    # Description  

    Demonstrate another collection of cards

    # Fixed by

    [[card1]]

We'll add a status to ``card`` by modifying the following file:

``scrum/backlog/card1.md``
"""""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: My first Scrum card
    status: Ready for Development
    ---


Next, we'll change the references in the config to suit our fields. Modify
``scrum.toml`` as follows:

.. code-block:: toml

    [tool.scrummd]
    strict = true
    scard_reference_format = "$index [$status]"

    [tool.scrummd.fields]
    severity = ["High", "Medium", "Low"]
    status = ["Ready For Development", "In Progress", "Done"]

We added a reference format, and expected values for the status.

Now, if we go ``scard bug1``, we'll see:

.. code-block:: text

    $ scard bug1
    ---
    bug1: Bug with project
    ---
    reporter: example@example.com
    severity: High
    description: Demonstrate another collection of cards
    fixed by: 
    card1 - My first Scrum card [Ready for Development]

You'll see that the reference has been replaced with a more useful reference.

Filters
^^^^^^^

Now you've got some bugs (sorry), you might want to see just the highest
severity bugs. ``sbl`` has filters available with ``--include``.

You can add multiple filters with multiple ``--include`` statements (all of
which must be matched to show), and multiple values to ``include`` by separating
them with a comma. If you were to go:

.. code-block:: text

    $ sbl --include severity=high
    index, summary
    bug3, Bad bug
    bug1, Bug with project

You can see that just high severity bugs are returned. Alternatively - you could
go ``sbl --include severity=high,medium`` to show all medium and high bugs.

Sorting
^^^^^^^

Sorting can be a helpful thing to do.  If instead of filtering our bugs, we
wanted to sort them priority, we can use ``--sort-by`` statements.

.. code-block:: text

    $ sbl --sort-by severity --columns "index, summary, severity"
    index, summary, severity
    card1, My first Scrum card,
    bug3, Bad bug, High
    bug1, Bug with project, High
    bug2, Bug with project 2, Low

Multiple ``--sort-by`` statements can be combined, and you can use ``^`` to
reverse the order.

.. code-block:: text

    $ sbl --sort-by ^severity --columns "index, summary, severity"
    index, summary, severity
    bug2, Bug with project 2, Low
    bug3, Bad bug, High
    bug1, Bug with project, High
    card1, My first Scrum card,

Tags
^^^^

Cards can be added to additional collections by 'tagging' them. If you add a
``tags`` field, any listed values will be created as a collection. Modify
the following cards as follows:

``scrum/reports/bug1.md``
"""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: Bug with project
    reporter: example@example.com
    severity: High
    ---

    # Tags

    - tool1
    - priority

    # Description  

    Demonstrate another collection of cards

    # Fixed by

    [[card1]]


``scrum/backlog/card1.md``
"""""""""""""""""""""""""""

.. code-block:: markdown

    ---
    summary: My first Scrum card
    status: Ready for Development
    ---

    # Tags

    - priority


Now, if you were to call ``sbl priority``, you would get the cards with that
tag.

.. code-block:: text

    $ sbl priority
    index, summary
    card1, My first Scrum card
    bug1, Bug with project 


Card defined collections
^^^^^^^^^^^^^^^^^^^^^^^^

Cards can define their own collections and sub-collections. Any time a card
is referenced in a field, that field an be used as a collection. For instance,
if you've been following this tutorial, ``bug1`` has a collection called
``bug1.fixed by`` due to ``[[card1]]`` being in the ``fixed by`` field:

.. code-block:: text

    $ sbl "bug1.fixed by"
    index, summary
    card1, My first Scrum card
    bug1, Bug with project 

Further - as all sub-collections are included in their parent collections,
``bug1`` is a collection by itself:

.. code-block:: text

    $ sbl bug1
    index, summary
    card1, My first Scrum card
    bug1, Bug with project 

You can create an ``items`` field if you wish to add cards to the collection
without creating a sub-collection.

Conclusion
^^^^^^^^^^

You have seen how to set up a basic repository, do some basic configuration,
add some cards, and seen some ways of interacting with them.

There should be enough tools here for you to go off and start managing your
cards with ScrumMD.
