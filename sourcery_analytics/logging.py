import logging

import rich.logging

from sourcery_analytics.cli.choices import OutputChoice


def set_up_logging(output: OutputChoice):
    if output is OutputChoice.rich:
        logging.basicConfig(format="%(message)s", handlers=[rich.logging.RichHandler()])
    else:
        logging.basicConfig()
