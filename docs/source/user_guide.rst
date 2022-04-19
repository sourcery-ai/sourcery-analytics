##########
User Guide
##########

:Created: 2022-04-19
:Last Updated: 2022-04-19


Using the CLI
=============

Basic Analysis
--------------

Analyze methods in a single Python file:

.. code-block::

   sourcery-analytics analyze path/to/file.py

Analyze all methods in all Python files in a directory:

.. code-block::

   sourcery-analytics analyze path/to/directory/

Rich Display
------------

By default, the analysis results are displayed in a rich text format in the command line.
To suppress this behaviour, use the ``--output`` option to select plain Python output.

.. code-block::

   sourcery-analytics analyze path/to/file.py --output plain

Metrics
-------

By default, all metrics are enabled, including providing the method's qualified name.
To limit to a single metric, use the ``--method-metric`` option:

.. code-block::

   sourcery-analytics analyze path/to/file.py --method-metric cyclomatic_complexity

Or, to use some subset of the available metrics, repeat the option:

.. code-block::

   sourcery-analytics analyze path/to/file.py --method-metric cyclomatic_complexity --method-metric cognitive_complexity

Collector
---------

By default, metrics for each method are collected in a dictionary. You can change this behaviour
by specifying the ``--collector`` option:

.. code-block::

   sourcery-analytics analyze path/to/file.py --collector tuple --no-use-rich

This might be useful if you need to write the output to a file, for instance.

Aggregation
-----------

By default, metrics are calculated for every method individually. You can instead aggregate the metrics
by specifying the ``--aggregation`` option:

.. code-block::

   sourcery-analytics analyze path/to/file.py --aggregation average

The peak value will show the maximum value of the metric for every method.
Note that for string "metrics", such as the qualified name of the method, this will just be the highest value
in alphabetical order.

.. code-block::

   sourcery-analytics analyze path/to/file.py --aggregation peak


Using the library
=================

Conditions
----------

Conditions are functions which operate on nodes to return a boolean. For instance, the following function
is a method.

.. doctest::

   >>> import astroid
   >>> def is_method_named_foo(node: astroid.nodes.NodeNG):
   ...     return isinstance(node, astroid.nodes.FunctionDef) and node.name == "foo"

Checking the type of node is very common, so there's a higher-order function available to construct
a condition for this:

.. doctest::

   >>> from sourcery_analytics.conditions import is_type
   >>> is_method = is_type(astroid.nodes.FunctionDef)
   >>> node = astroid.extract_node("def foo(): pass")
   >>> is_method(node)
   True

.. hint::

   Why is this different to `isinstance`? ``is_type`` is a *higher-order* function, meaning it returns
   a function, in this case a condition, which means we can pass the result to other functions which
   expect conditions, and saves us writing lots of ``lambda node: ...`` expressions.

Extractors
----------

:py:class:`.Extractor`\ s take a condition and extract nodes satisfying the condition. They can be used in order to,
for instance, extract constants from an expression or methods from a module.

.. doctest::

   >>> from sourcery_analytics.extractors import Extractor
   >>> method_extractor = Extractor.from_condition(is_method)
   >>> source = astroid.parse(
   ...     '''
   ...         def one():
   ...             return 1
   ...         def two():
   ...             return 2
   ...     '''
   ... )
   >>> methods = method_extractor.extract(source)
   >>> [method.name for method in methods]
   ['one', 'two']
   >>> const_extractor = Extractor.from_condition(is_type(astroid.nodes.Const))
   >>> consts = const_extractor.extract(source)
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
   >>> method = astroid.extract_node(
   ...     '''
   ...         def slow_sum(xs):
   ...             result = 0
   ...             for x in xs:
   ...                 result = result + x
   ...             return result
   ...     '''
   ... )
   >>> method_name(method)
   'slow_sum'
   >>> method_length(method)
   3
   >>> method_cognitive_complexity(method)
   1

Metrics can be combined using Collector functions. Collectors take several metrics and combine them
into a single metric.

.. doctest::

   >>> from sourcery_analytics.metrics.collectors import name_metrics
   >>> named_metrics = name_metrics(method_name, method_length, method_cognitive_complexity)
   >>> named_metrics(method)
   {'method_name': 'slow_sum', 'method_length': 3, 'method_cognitive_complexity': 1}


Aggregations
------------

Aggregations are ways to combine the metrics from several methods. The simplest "aggregation"
is just to collect the results in a list:

.. doctest::

   >>> from sourcery_analytics.aggregations import collect
   >>> method_extractor = Extractor.from_condition(is_method)
   >>> source = astroid.parse(
   ...     '''
   ...         def one():
   ...             return 1
   ...         def two(n):
   ...             if n == 2:
   ...                 return n
   ...     '''
   ... )
   >>> methods = list(method_extractor.extract(source))
   >>> collected = collect(method_cognitive_complexity)
   >>> collected(methods)
   [0, 1]

You can also aggregate using the average, total, or peak ("maximum") values, and combined metrics are supported.

.. doctest::

   >>> from sourcery_analytics.aggregations import average
   >>> averaged = average(named_metrics)
   >>> sorted(averaged(methods))  # sorted allows doctests to pass
   [('method_cognitive_complexity', 0.5), ('method_length', 1.0), ('method_name', None)]

Analyzers
---------

Analyzers are a combination of a metric with an aggregation. They are convenient to construct and use
for large-scale analysis of methods.

.. doctest::

   >>> from sourcery_analytics.analysis import Analyzer
   >>> analyzer = Analyzer.from_metrics(method_name, method_length, method_cognitive_complexity)
   >>> records = analyzer.analyze(methods)
   >>> records
   [{'method_name': 'one', 'method_length': 1, 'method_cognitive_complexity': 0}, {'method_name': 'two', 'method_length': 1, 'method_cognitive_complexity': 1}]

For further analysis, results like this can be readily incorporated into, for example, a pandas dataframe:

.. doctest::

   >>> import pandas  # doctest: +SKIP
   >>> data = pandas.DataFrame.from_records(records)  # doctest: +SKIP

