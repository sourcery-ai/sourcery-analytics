###############
Developer Guide
###############

:Created: 2022-04-19
:Last Updated: 2022-04-28

This document aims to be a guide for those contributing to the repository by outlining the decisions taken
during its development and a description of the patterns used.


Local Development
=================

Prerequisites:

* ``git_`` for version control
* Python_ for development
* poetry_ for Python dependency management

Getting the source code
-----------------------

.. code-block::

   $ git clone git@github.com:sourcery-ai/sourcery-analytics.git

Install Dependencies
--------------------

From the top-level ``sourcery-analytics`` directory:

.. code-block::

   $ poetry install

.. note:: you should already have installed poetry_ as indicated in the prerequisites.

Run Tests
---------

From the top-level ``sourcery-analytics`` directory:

.. code-block::

   $ poetry run pytest

Build this documentation
------------------------

.. code-block::

   poetry run sphinx-apidoc -eMTf --templatedir ./docs/source/_templates/apidoc -o docs/source/api sourcery_analytics
   sphinx-build -b html docs/source docs/build

Run tests with coverage

.. code-block::

   pytest --cov

.. _git: https://git-scm.com/
.. _Python: https://www.python.org/
.. _poetry: https://python-poetry.org/


Parsing
=======

In order to analzye code, we need to parse it into a structure we can manipulate. Code is typically parsed
into an Abstract Syntax Tree, or AST [#]_. Python provides a standard implementation [#]_ to parse code into an AST,
but it misses features we need for analysis, most notably a link from a child node to its parent.

As a result, we've opted to use `astroid <https://github.com/PyCQA/astroid>`_ as the principal parser.
As well as providing an enhanced AST, astroid provides several convenient parsing functions which make testing
and developing interfaces much easier than the built-in Python parser.


Visitors
========

The Visitor pattern [#]_ is a well-known pattern for analyzing trees of any type. At a high-level,
it separates the calculation over elements (also known as *nodes*) within the tree from the calculation
handling the traversal of the tree.

For code analysis, we typically need to calculate some property of a node, such as its "complexity", with
respect to the context of the node, for instance whether or not it is in a conditional.

Underlying the high-level analysis in ``sourcery-analytics`` is a set of generic visitors which operate
on astroid's ASTs (see :py:mod:`.visitors`). Visitors implement two methods: ``_enter``, which handles the context,
and ``_touch`` which returns a "fact" about the node, based on the context. Keeping these separate helps us be very
clear about how the calculation works. For an example, see :py:mod:`.cognitive_complexity`, in which the visitor
increments its context penalty for nested structures, and returns the complexity of individual nodes.

What about walking the tree? Well, the list of sub-nodes of a node is a "fact" about that node, so we can implement
the walker as a visitor! This is the job of the :py:class:`.TreeVisitor` which is used throughout the codebase.
Let's dig a bit further into how the :py:class:`.TreeVisitor` works, as it's important for development.

The Tree Visitor
----------------

Consider this simple example:

.. doctest::

   >>> import astroid
   >>> from sourcery_analytics.visitors import TreeVisitor

   >>> src = '''
   ...     def add(x, y):
   ...         z = x + y
   ...         return z
   ... '''
   >>> node = astroid.extract_node(src)
   >>> tree_visitor = TreeVisitor()

By default, the :py:class:`.TreeVisitor` will return every sub-node of the node as an iterator.

.. doctest::

   >>> tree_visitor.visit(node)
   <generator object TreeVisitor._visit at 0x...>
   >>> list(tree_visitor.visit(node))
   [<FunctionDef.add l.2 at 0x...>, <Arguments l.2 at 0x...>, <AssignName.x l.2 at 0x...>, <AssignName.y l.2 at 0x...>, <Assign l.3 at 0x...>, <AssignName.z l.3 at 0x...>, <BinOp l.3 at 0x...>, <Name.x l.3 at 0x...>, <Name.y l.3 at 0x...>, <Return l.4 at 0x...>, <Name.z l.4 at 0x...>]

Instead of returning the nodes, we can use a sub-visitor to return alternative information.
One useful generic visitor is the :py:class:`.FunctionVisitor` which wraps a function for use as a visitor.
Let's return just the name of each node in the tree:

.. doctest::

   >>> from sourcery_analytics.visitors import FunctionVisitor
   >>> name_visitor = FunctionVisitor(lambda node: node.__class__.__name__)
   >>> tree_visitor = TreeVisitor(name_visitor)
   >>> list(tree_visitor.visit(node))
   ['FunctionDef', 'Arguments', 'AssignName', 'AssignName', 'Assign', 'AssignName', 'BinOp', 'Name', 'Name', 'Return', 'Name']

How about counting the nodes in the tree? The philosophy in sourcery-analytics is to break this down:

1. Question: what is number of nodes in *one* node? Answer: 1
2. Question: how do we aggregate in that case? Answer: :py:func:`sum`.

.. doctest::

   >>> tree_visitor = TreeVisitor(FunctionVisitor(lambda node: 1), sum)
   >>> tree_visitor.visit(node)
   11

Of course, there are other ways to calculate this, but the flexibility of the tree visitor means it is useful
throughout ``sourcery-analytics``. See the source for :py:mod:`.extractors`, :py:mod:`.analysis`, or
:py:mod:`.metrics.cognitive_complexity` for some examples.


References
==========

.. [#] https://en.wikipedia.org/wiki/Abstract_syntax_tree
.. [#] https://docs.python.org/3/library/ast.html
.. [#] https://en.wikipedia.org/wiki/Visitor_pattern