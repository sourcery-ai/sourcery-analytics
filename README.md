# Sourcery Analytics

![PyPI](https://img.shields.io/pypi/v/sourcery-analytics)

`sourcery-analytics` is a command line tool and library for statically analyzing Python code quality.

Get started by installing using `pip`:

```commandline
pip install sourcery-analytics
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

Alternatively, import and run analysis using the library:

```python
from sourcery_analytics import analyze_methods
source = """
    def cast_spell(self, spell):
        if self.power < spell.power:
            raise InsufficientPower
        print(f"{self.name} cast {spell.name}!")
"""
analyze_methods(source)
# [{'method_qualname': '.cast_spell', 'method_length': 3, 'method_cyclomatic_complexity': 1, 'method_cognitive_complexity': 1, 'method_working_memory': 6}]
```

For more, see the [docs](https://sourcery-analytics.sourcery.ai/).

### Repoanalysis.com
You can see how hundreds of top projects measure across different code quality metrics and see how your priojects compare at [repoanalysis.com](https://repoanalysis.com/)

### Developed by Sourcery
Sourcery Analytics was originally developed by the team at [Sourcery](https://sourcery.ai/?utm_source=sourcery-analytics). Sourcery is an automated coding assistant to help Python developers review and improve their code while they work. Sourcery has a built in library of 100+ core rules and you can extend it further to create custom rules for any scenario.
