import pytest

from sourcery_analytics.settings import Settings
from sourcery_analytics.utils import clean_source


@pytest.fixture
def toml_file_path(tmp_path):
    return tmp_path / "pyproject.toml"


@pytest.fixture
def toml_file(toml_file_path):
    toml_file_path.write_text(
        clean_source(
            """
                [tool.sourcery-analytics.max]
                method_cyclomatic_complexity = 10
            """
        )
    )


class TestSettings:
    def test_default(self):
        settings = Settings()
        assert settings.metric_thresholds.cyclomatic_complexity == 15

    def test_from_toml_file(self, toml_file, toml_file_path):
        settings = Settings.from_toml_file(toml_file_path)
        assert settings.metric_thresholds.cyclomatic_complexity == 10
