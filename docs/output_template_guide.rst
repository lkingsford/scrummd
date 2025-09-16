Output Template Guide
~~~~~~~~~~~~~~~~~~~~~

Basic information
=================

The templates are in jinja2 form. 

Exposed fields
==============

.. autoclass:: scrummd.formatter.TemplateFields
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:


Replaceable macros
==================

Purpose
-------

Replaceable macros offer hooks into some particular functionality to provide
more control over formatting. They must be define with exactly the parameters
listed here to function. 

``card_ref``
------------

Description
^^^^^^^^^^^

Used to format any card references inside a field.

Parameters
^^^^^^^^^^

``component``
"""""""""""""

The :class:`scrummd.source\_md.CardComponent` that is being expanded. The
``card`` will be ``none`` if the card is not found.

Default
^^^^^^^

``[[ {{ component.card_index }} ]]``

Setting as default
==================

``default_<program>.j2``
------------------------

Each program searches:

-   the current working directory;
-   the ``.templates`` directory in the ``scrum_path``
-   the ``templates`` directory in the ``scrum_path``
-   ``templates`` in the scrummd package;

for ``default_<program>.j2``. For instance, if you add a file called
``default_scard.j2`` to ``<scrum_path>/templates``, it will overwrite the default
template.

In Configuration
----------------

Configuration overrides the implicit ``default_<program>.j2`` templates.

Define the ``scard`` default template with
:ref:`configuration-scard-default-template`.


Example template
================

.. literalinclude:: ../scrummd/templates/default_scard.j2
   :language: jinja2
   :linenos: