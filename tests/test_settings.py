from sourcery_analytics.settings import Settings


class TestSettings:
    def test_default(self):
        settings = Settings()
        assert settings.thresholds.method_cyclomatic_complexity == 10

    def test_from_toml_file(self, toml_file, toml_file_path):
        settings = Settings.from_toml_file(toml_file_path)
        assert settings.thresholds.method_cyclomatic_complexity == 5
