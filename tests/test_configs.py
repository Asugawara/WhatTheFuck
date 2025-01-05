import tempfile
from dataclasses import asdict
from unittest.mock import mock_open, patch

import pytest

from wtf.configs import WTF_CONFIG_PATH, Config


def test_config_postinit_validation():
    with pytest.raises(ValueError):
        Config(terminal_prompt_lines=0)
    with pytest.raises(ValueError):
        Config(command_output_logger="script-pty")
    with pytest.raises(ValueError):
        Config(model="test-model")
    with pytest.raises(ValueError):
        Config(model="gpt-4o-mini", openai_api_key="")
    with pytest.raises(ValueError):
        Config(model="claude-3-5-sonnet-20241022", anthropic_api_key="")
    with pytest.raises(ValueError):
        Config(prompt_path="test-prompt-path")


@patch("builtins.open", new_callable=mock_open)
def test_config_save(mock_open):
    with patch("json.dump") as mock_json_dump:
        config = Config(model="gpt-4o-mini", openai_api_key="test_openai_key")
        # When post init, config is saved to the file
        mock_open.assert_called_once_with(WTF_CONFIG_PATH, "w")
        mock_json_dump.assert_called_once_with(asdict(config), mock_open(), indent=4)


def test_config_from_file():
    with tempfile.NamedTemporaryFile("w") as tmp_config:
        with (
            patch("wtf.configs.WTF_CONFIG_PATH", tmp_config.name),
            patch("os.path.exists", return_value=True),
            patch("os.getenv", return_value="test_key"),
        ):
            config = Config(model="gpt-4o-mini", openai_api_key="test_key")
            config_from_file = Config.from_file(tmp_config.name)
            assert config_from_file.model == "gpt-4o-mini"
            assert config_from_file.openai_api_key == "test_key"
            assert config_from_file == config
