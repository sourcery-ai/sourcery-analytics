"""Logging set-up for the command-line interface."""
import logging

import rich.logging

from sourcery_analytics.cli.choices import OutputChoice


def set_up_logging(output: OutputChoice):
    """Sets up logging for "rich" or basic output, automatically capturing warnings."""
    if output is OutputChoice.RICH:
        logging.basicConfig(format="%(message)s", handlers=[rich.logging.RichHandler()])
    else:
        logging.basicConfig()
    logging.captureWarnings(True)
