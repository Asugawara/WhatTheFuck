import tempfile
from dataclasses import asdict
from unittest.mock import mock_open, patch

import pytest

from wtf.configs import WTF_CONFIG_PATH, Config


def test_config_validations():
    with pytest.raises(ValueError):
        config = Config(terminal_prompt_lines=0)
        config.validate()
    with pytest.raises(ValueError):
        config = Config(command_output_logger="script-pty")
        config.validate()
    with pytest.raises(ValueError):
        config = Config(model="test-model")
        config.validate()
    with pytest.raises(ValueError):
        config = Config(model="gpt-4o-mini", openai_api_key="")
        config.validate()
    with pytest.raises(ValueError):
        config = Config(model="claude-3-5-sonnet-20241022", anthropic_api_key="")
        config.validate()
    with pytest.raises(FileNotFoundError):
        config = Config(prompt_path="test-prompt-path", openai_api_key="test")
        config.validate()


@patch("builtins.open", new_callable=mock_open)
def test_config_save(mock_open):
    with patch("json.dump") as mock_json_dump:
        config = Config(model="gpt-4o-mini", openai_api_key="test_openai_key")
        config.save()
        mock_open.assert_called_once_with(WTF_CONFIG_PATH, "w")
        mock_json_dump.assert_called_once_with(asdict(config), mock_open(), indent=4)


def test_config_from_file():
    with tempfile.NamedTemporaryFile("w") as tmp_config:
        with (
            patch("wtf.configs.WTF_CONFIG_PATH", tmp_config.name),
            patch("os.path.exists", return_value=True),
        ):
            config = Config(model="gpt-4o-mini", openai_api_key="test_key", anthropic_api_key="test_key")
            config.validate()
            config_from_file = Config.from_file(tmp_config.name)
            assert config_from_file.model == "gpt-4o-mini"
            assert config_from_file.openai_api_key == "test_key"
            assert config_from_file == config
