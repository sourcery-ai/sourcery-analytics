# Sourcery Analytics

`sourcery-analytics` is a command line tool and library for statically analyzing Python code quality.

Get started by installing using `pip`:

```commandline
pip install sourcery_analytics
```

This will install `sourcery-analytics` as a command-line tool.
To analyze a single Python file, use the `analyze` subcommand:

```commandline
sourcery-analytics analyze path/to/file.py
```

Example:

```commandline
sourcery-analytics analyze sourcery_analytics/analysis.py
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Method                                      ┃ length ┃ cyclomatic_complexity ┃ cognitive_complexity ┃ working_memory ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ sourcery_analytics.analysis.analyze         │      5 │                     1 │                    0 │              8 │
│ sourcery_analytics.analysis.analyze_methods │      4 │                     1 │                    1 │             12 │
└─────────────────────────────────────────────┴────────┴───────────────────────┴──────────────────────┴────────────────┘
```

For more, see the [docs]().