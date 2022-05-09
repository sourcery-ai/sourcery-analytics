import pathlib

import pydantic
import tomli


class ThresholdSettings(pydantic.BaseModel):
    method_length: pydantic.PositiveInt = 15
    method_cyclomatic_complexity: pydantic.PositiveInt = 10
    method_cognitive_complexity: pydantic.PositiveInt = 10
    method_working_memory: pydantic.PositiveInt = 20

    class Config:
        extras_allowed = True


class Settings(pydantic.BaseSettings):
    thresholds: ThresholdSettings = ThresholdSettings()

    @classmethod
    def from_toml_file(cls, toml_file_path: pathlib.Path):
        with toml_file_path.open("rb") as f:
            config = tomli.load(f)
        final = cls().dict() | config.get("tool", {}).get("sourcery-analytics", {})
        return cls(**final)
