##########
User Guide
##########

:Created: 2022-04-19
:Last Updated: 2022-08-22


Command-Line Analysis
=====================


Basic Analysis
--------------

Analyze methods in a single Python file:

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/analysis.py

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
   ┃                                    qualname ┃ length ┃ cyclomatic_complexity ┃ cognitive_complexity ┃ working_memory ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
   │      sourcery_analytics.analysis.break_down │      8 │                     5 │                    3 │             17 │
   │ sourcery_analytics.analysis.analyze_methods │      4 │                     1 │                    1 │             12 │
   │         sourcery_analytics.analysis.analyze │      4 │                     1 │                    0 │              7 │
   └─────────────────────────────────────────────┴────────┴───────────────────────┴──────────────────────┴────────────────┘


Analyze all methods in all Python files in a directory:

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/metrics

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
   ┃                                                                            qualname ┃ length ┃ cyclomatic_complexity ┃ cognitive_complexity ┃ working_memory ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
   │                     sourcery_analytics.metrics.working_memory.method_working_memory │      2 │                     0 │                    0 │              6 │
   │                                 sourcery_analytics.metrics.working_memory.get_names │      1 │                     0 │                    0 │              4 │
   │                                  sourcery_analytics.metrics.working_memory.get_name │      7 │                     3 │                    3 │              7 │
   │               sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor._touch │     11 │                     4 │                    4 │             13 │
   │               sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor._enter │      9 │                     3 │                    3 │             16 │
   │             sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor.__name__ │      1 │                     0 │                    0 │              1 │
   │             sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor.__init__ │      4 │                     1 │                    1 │              6 │
   │                                     sourcery_analytics.metrics.utils.node_type_name │      1 │                     0 │                    0 │              3 │
   │                                    sourcery_analytics.metrics.utils.method_qualname │      1 │                     0 │                    0 │              2 │

   [Result truncated]


Output Options
--------------

Plain Python Output
~~~~~~~~~~~~~~~~~~~

By default, the analysis results are displayed in a rich text format in the command line.
To suppress this behaviour, use the ``--output`` option to select plain Python output.

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/utils.py --output plain

.. code-block::

   [{'method_qualname': 'sourcery_analytics.utils.nodedispatch.wrapped', 'method_length': 9, 'method_cyclomatic_complexity': 3, 'method_cognitive_complexity': 3, 'method_working_memory': 9}, {'method_qualname': 'sourcery_analytics.utils.nodedispatch', 'method_length': 11, 'method_cyclomatic_complexity': 3, 'method_cognitive_complexity': 3, 'method_working_memory': 10}, {'method_qualname': 'sourcery_analytics.utils.clean_source', 'method_length': 1, 'method_cyclomatic_complexity': 0, 'method_cognitive_complexity': 0, 'method_working_memory': 4}]

CSV Output
~~~~~~~~~~

Alternatively, you can output in CSV format.

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/utils.py --output csv

.. code-block::

   qualname,length,cyclomatic_complexity,cognitive_complexity,working_memory
   sourcery_analytics.utils.nodedispatch,11,3,3,10
   sourcery_analytics.utils.nodedispatch.wrapped,9,3,3,9
   sourcery_analytics.utils.clean_source,1,0,0,4

This can be readily dumped to a file using the command line:

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/utils.py --output csv > utils_metrics.csv


Metrics
-------

By default, all metrics are enabled, including providing the method's qualified name.
To limit to a single metric, use the ``--method-metric`` option:

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/conditions.py --method-metric cyclomatic_complexity

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Method                                         ┃ cyclomatic_complexity ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
   │ sourcery_analytics.conditions.is_elif          │                     4 │
   │ sourcery_analytics.conditions.always           │                     0 │
   │ sourcery_analytics.conditions.is_type          │                     0 │
   │ sourcery_analytics.conditions.is_type._is_type │                     0 │
   └────────────────────────────────────────────────┴───────────────────────┘

Or, to use some subset of the available metrics, repeat the option:

.. code-block::

   $ sourcery-analytics analyze sourcery_analytics/conditions.py --method-metric cyclomatic_complexity --method-metric cognitive_complexity

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Method                                         ┃ cyclomatic_complexity ┃ cognitive_complexity ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
   │ sourcery_analytics.conditions.is_elif          │                     4 │                    0 │
   │ sourcery_analytics.conditions.always           │                     0 │                    0 │
   │ sourcery_analytics.conditions.is_type          │                     0 │                    0 │
   │ sourcery_analytics.conditions.is_type._is_type │                     0 │                    0 │
   └────────────────────────────────────────────────┴───────────────────────┴──────────────────────┘


Sorting
-------

By default, the result is sorted by the first metric specified.
You can sort using any of the specified metrics using the ``--sort`` option:

.. code-block::

   $ sourcery-analytics analyze path/to/file.py --sort cognitive_complexity

.. code-block::

   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
   ┃ Method                                                                              ┃ length ┃ cyclomatic_complexity ┃ cognitive_complexity ┃ working_memory ┃
   ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
   │ sourcery_analytics.metrics.cyclomatic_complexity.cyclomatic_complexity              │     13 │                     7 │                    6 │             34 │
   │ sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor._touch               │     11 │                     4 │                    4 │             13 │
   │ sourcery_analytics.metrics.cognitive_complexity.CognitiveComplexityVisitor._enter   │      7 │                     3 │                    3 │             13 │
   │ sourcery_analytics.metrics.working_memory.WorkingMemoryVisitor._enter               │      9 │                     3 │                    3 │             16 │
   │ sourcery_analytics.metrics.working_memory.get_name                                  │      7 │                     3 │                    3 │              7 │
   │ sourcery_analytics.metrics.compounders._CompoundMetric.addone                       │      6 │                     3 │                    2 │              7 │

   [Result truncated]


.. note:: If you're specifying both ``--method-metrics`` and ``--sort``, you should ensure the sort value is one of the specified metrics.


Command-Line Assessment
=======================

The "assess" command will return a non-zero exit code if it finds functions exceeding threshold values.


Assess Metrics
--------------

Identify functions exceeding metric thresholds.

.. code-block::

   $ sourcery-analytics assess sourcery-analytics/metrics

.. code-block::

   sourcery_analytics/metrics/cyclomatic_complexity.py:47: error: working_memory of cyclomatic_complexity is 34 exceeding threshold of 20
   Found 1 errors.


Setting Thresholds
------------------

You can customise the error thresholds by adding the following section to your ``pyproject.toml`` file.
The values shown here are the defaults.

.. code-block:: toml

   # other settings...

   [tool.sourcery-analytics]

   [tool.sourcery-analytics.thresholds]
   method_length = 15
   method_cyclomatic_complexity = 10
   method_cognitive_complexity = 10
   method_working_memory = 20


Choosing Metrics
----------------

Select a sub-set of metrics to assess using a (optionally repeated) ``--method-metric`` option:

.. code-block::

   $ sourcery-analytics assess sourcery_analytics/metrics --method-metric cyclomatic_complexity --method-metric cognitive_complexity

.. code-block::

   Assessment Complete
   No issues found.


Custom Settings File
--------------------

If you don't have a ``pyproject.toml`` file, you can provide a custom ``.toml`` file to read thresholds from:

.. code-block::

   $ sourcery-analytics assess sourcery_analytics/metrics --settings-file thresholds.toml


Using the library
=================

Analysis
--------

In :py:mod:`.analysis` there are several high-level functions for calculating, and optionally aggregating, metric results over a collection of nodes.
To perform analysis like the CLI commands described above, use these functions.

For more details about how these functions work, keep reading below.

.. doctest::

   >>> from sourcery_analytics.analysis import analyze_methods
   >>> from sourcery_analytics.metrics import method_name, method_length, method_cognitive_complexity
   >>> source = '''
   ...     def one():
   ...         return 1
   ...     def two(n):
   ...         if n == 2:
   ...             return n
   ... '''
   >>> records = analyze_methods(source, metrics=(method_name, method_length, method_cognitive_complexity))
   >>> records
   [{'method_name': 'one', 'method_length': 1, 'method_cognitive_complexity': 0}, {'method_name': 'two', 'method_length': 2, 'method_cognitive_complexity': 1}]

For further analysis, results like this can be readily incorporated into, for example, a pandas dataframe:

.. doctest::

   >>> import pandas  # doctest: +SKIP
   >>> data = pandas.DataFrame.from_records(records)  # doctest: +SKIP

Conditions
----------

Conditions are functions which operate on nodes to return a boolean. For instance, the following function
is a condition.

.. doctest::

   >>> import astroid
   >>> def is_method_named_foo(node: astroid.nodes.NodeNG) -> bool:
   ...     return isinstance(node, astroid.nodes.FunctionDef) and node.name == "foo"

Checking the type of node is very common, so there's a higher-order function available to construct
a condition for this:

.. doctest::

   >>> from sourcery_analytics.conditions import is_type
   >>> is_method = is_type(astroid.nodes.FunctionDef)
   >>> node = astroid.extract_node("def foo(): pass")
   >>> is_method(node)
   True

A couple of common type-checks, including ``is_method`` and ``is_name`` are included in the :py:mod:`.conditions` module.

.. hint::

   Why is this different to `isinstance`? ``is_type`` is a *higher-order* function, meaning it returns
   a function, in this case a condition, which means we can pass the result to other functions which
   expect conditions, and saves us writing lots of ``lambda node: ...`` expressions.

Extracting
----------

:py:class:`.Extractor`\ s take a condition and extract nodes satisfying the condition. They can be used in order to,
for instance, extract constants from an expression or methods from a module. Extractors can be used directly or through
their high-level interface :py:meth:`.extract`.

.. doctest::

   >>> from sourcery_analytics.extractors import extract
   >>> source = '''
   ...     def one():
   ...         return 1
   ...     def two():
   ...         return 2
   ... '''
   >>> methods = extract(source, condition=is_method)
   >>> [method.name for method in methods]
   ['one', 'two']
   >>> consts = extract(source, condition=is_type(astroid.nodes.Const))
   >>> [const.value for const in consts]
   [1, 2]


Metrics
-------

A metric is a "fact" about a node, typically a numeric value. Some metrics are simple,
for instance the number of statements in a method or the number of handlers in a try/except block.
These can be implemented as functions of the node.

Other metrics depend on context, such as the depth of the node. Where the context matters,
metrics are implemented as a :py:class:`.Visitor` class.

*Method* metrics are special functions that calculate metrics over a whole method.
In ``sourcery_analytics.metrics``, these are prefixed with ``method_`` for clarity.
As well as numerical metrics, several utility metrics (such as to get the method name) are provided.

.. doctest::

   >>> from sourcery_analytics.metrics import method_name, method_length, method_cognitive_complexity
   >>> method = '''
   ...     def slow_sum(xs):
   ...         result = 0
   ...         for x in xs:
   ...             result = result + x
   ...         return result
   ... '''
   >>> method_name(method)
   'slow_sum'
   >>> method_length(method)
   4
   >>> method_cognitive_complexity(method)
   1

Metrics can be compounded using Compounder functions. Compounders take several metrics and combine them
into a single metric.

.. doctest::

   >>> from sourcery_analytics.metrics.compounders import name_metrics
   >>> named_metrics = name_metrics(method_name, method_length, method_cognitive_complexity)
   >>> named_metrics(method)
   {'method_name': 'slow_sum', 'method_length': 4, 'method_cognitive_complexity': 1}


Aggregations
------------

Aggregations are ways to combine the metrics from several methods. The simplest "aggregation"
is just to collect the results in a list:

.. doctest::

   >>> source = '''
   ...     def one():
   ...         return 1
   ...     def two(n):
   ...         if n == 2:
   ...             return n
   ... '''
   >>> methods = list(extract(source, condition=is_method))
   >>> results = (method_length(method) for method in methods)
   >>> list(results)
   [1, 2]

You can also aggregate using the average, total, or peak ("maximum") values, and combined metrics are supported.

.. doctest::

   >>> from sourcery_analytics.metrics.aggregations import average
   >>> results = (named_metrics(method) for method in methods)
   >>> sorted(average(results))  # sorted allows doctests to pass
   [('method_cognitive_complexity', 0.5), ('method_length', 1.5), ('method_name', None)]

