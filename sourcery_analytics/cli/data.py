"""Models holding data for the command line, such as analysis results."""
import dataclasses
import pathlib
import typing

from sourcery_analytics.settings import ThresholdSettings


class ThresholdBreachDict(typing.TypedDict):
    """A dictionary describing a single threshold breach within a single method."""

    metric_name: str
    method_file: typing.Union[str, pathlib.Path]
    method_lineno: int
    method_name: str
    metric_value: int


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
        threshold_breach_dict: ThresholdBreachDict,
        threshold_settings: ThresholdSettings,
    ) -> "ThresholdBreach":
        """Constructs a ThresholdBreach instance from a dictionary."""
        metric_name = threshold_breach_dict["metric_name"]
        try:  # get relative path
            path = pathlib.Path(threshold_breach_dict["method_file"]).relative_to(
                pathlib.Path.cwd().absolute()
            )
        except ValueError:  # fall back to absolute path
            path = pathlib.Path(threshold_breach_dict["method_file"])
        return ThresholdBreach(
            path,
            threshold_breach_dict["method_lineno"],
            threshold_breach_dict["method_name"],
            metric_name.removeprefix("method_"),
            threshold_breach_dict["metric_value"],
            threshold_settings.dict()[metric_name],
        )
