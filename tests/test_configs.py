import tempfile
from unittest.mock import mock_open, patch

import pytest
from pydantic import ValidationError

from wtf.configs import WTF_CONFIG_PATH, Config


def test_config_validations():
    with pytest.raises(ValidationError):
        config = Config(terminal_prompt_lines=0)
    with pytest.raises(ValidationError):
        config = Config(command_output_logger="script-pty")
    with pytest.raises(ValidationError):
        config = Config(model="test-model")

    with pytest.raises(RuntimeError):
        config = Config(model="gpt-4o-mini", openai_api_key="")
        config.validate_config()
    with pytest.raises(RuntimeError):
        config = Config(model="claude-3-5-sonnet-20241022", anthropic_api_key="")
        config.validate_config()
    with pytest.raises(FileNotFoundError):
        config = Config(prompt_path="test-prompt-path", openai_api_key="test")
        config.validate_config()


@patch("builtins.open", new_callable=mock_open)
def test_config_save(mock_open):
    with patch("json.dump") as mock_json_dump:
        config = Config(model="gpt-4o-mini", openai_api_key="test_openai_key")
        config.save()
        mock_open.assert_called_once_with(WTF_CONFIG_PATH, "w")
        mock_json_dump.assert_called_once_with(config.model_dump(), mock_open(), indent=4)


def test_config_from_file():
    with tempfile.NamedTemporaryFile("w") as tmp_config:
        with (
            patch("wtf.configs.WTF_CONFIG_PATH", tmp_config.name),
            patch("os.path.exists", return_value=True),
        ):
            config = Config(model="gpt-4o-mini", openai_api_key="test_key", anthropic_api_key="test_key")
            config.validate_config()
            config_from_file = Config.from_file(tmp_config.name)
            assert config_from_file.model == "gpt-4o-mini"
            assert config_from_file.openai_api_key == "test_key"
            assert config_from_file == config
