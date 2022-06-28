"""Models holding data for the command line, such as analysis results."""
import dataclasses
import pathlib
import typing

from sourcery_analytics.settings import ThresholdSettings


@dataclasses.dataclass
class ThresholdBreach:
    """A model describing a single threshold breach within a single method."""

    relative_path: pathlib.Path
    lineno: int
    method_name: str
    metric_name: str
    metric_value: int
    threshold_value: int

    @classmethod
    def from_dict(
        cls,
        d: typing.Dict[str, typing.Any],
        threshold_settings: ThresholdSettings,
    ) -> "ThresholdBreach":
        """Constructs a ThresholdBreach instance from a dictionary."""
        metric_name = d["metric_name"]
        try:  # get relative path
            path = pathlib.Path(d["method_file"]).relative_to(
                pathlib.Path.cwd().absolute()
            )
        except ValueError:  # fall back to absolute path
            path = pathlib.Path(d["method_file"])
        return ThresholdBreach(
            path,
            d["method_lineno"],
            d["method_name"],
            metric_name.removeprefix("method_"),
            d["metric_value"],
            threshold_settings.dict()[metric_name],
        )
