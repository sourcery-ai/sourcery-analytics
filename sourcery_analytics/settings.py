import pathlib

import pydantic
import tomli


class MetricThresholdSettings(pydantic.BaseModel):
    cyclomatic_complexity: int = 15


class Settings(pydantic.BaseSettings):
    metric_thresholds: MetricThresholdSettings = MetricThresholdSettings()

    @classmethod
    def from_toml_file(cls, toml_file_path: pathlib.Path):
        with toml_file_path.open("rb") as f:
            config = tomli.load(f)
        return cls(**config.get("tool", {}).get("sourcery-analytics", {}))
