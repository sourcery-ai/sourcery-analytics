"""Models describing sourcery-analytics settings."""
import pathlib

import pydantic
import tomli


class ThresholdSettings(pydantic.BaseModel):
    """Model describing the available thresholds and their defaults."""

    method_length: pydantic.PositiveInt = 15
    method_cyclomatic_complexity: pydantic.PositiveInt = 10
    method_cognitive_complexity: pydantic.PositiveInt = 10
    method_working_memory: pydantic.PositiveInt = 20


class Settings(pydantic.BaseSettings):
    """Model describing general sourcery-analytics settings and their construction."""

    thresholds: ThresholdSettings = ThresholdSettings()

    @classmethod
    def from_toml_file(cls, toml_file_path: pathlib.Path):
        """Construct settings from a toml file.

        Args:
            toml_file_path:
                Relative or fully-qualified path to a toml file containing
                sourcery-analytics settings.

        Returns:
            A Settings instance.

        """
        with toml_file_path.open("rb") as file:
            config = tomli.load(file)
        final = cls().dict() | config.get("tool", {}).get("sourcery-analytics", {})
        return cls(**final)
