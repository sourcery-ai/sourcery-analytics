import dataclasses
import pathlib
import typing

from sourcery_analytics.settings import ThresholdSettings


@dataclasses.dataclass
class ThresholdBreach:
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
    ):
        metric_name = d["metric_name"].removeprefix("method_")
        return ThresholdBreach(
            pathlib.Path(d["method_file"]).relative_to(pathlib.Path.cwd().absolute()),
            d["method_lineno"],
            d["method_name"],
            metric_name,
            d["metric_value"],
            threshold_settings.dict()[metric_name],
        )
