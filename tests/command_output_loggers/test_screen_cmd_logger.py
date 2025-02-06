import hashlib
from unittest.mock import patch, mock_open, MagicMock

import pytest

from wtf.command_output_loggers.base import CommandOutput
from wtf.command_output_loggers.screen_cmd_logger import ScreenCmdLogger
from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER


@pytest.fixture
def screen_cmd_logger():
    return ScreenCmdLogger(logfile="test_logfile.log")


def test_session_name(screen_cmd_logger):
    expected_session_name = hashlib.sha256("test_logfile.log".encode()).hexdigest()
    assert screen_cmd_logger.session_name == expected_session_name


@patch("subprocess.run")
def test_begin(mock_subprocess_run, screen_cmd_logger):
    screen_cmd_logger.begin()
    mock_subprocess_run.assert_called_once_with(
        ["screen", "-q", "-S", screen_cmd_logger.session_name, "-L", "-Logfile", "test_logfile.log"]
    )


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=b"prompt$(wtf): command\ncommand output\nprompt$(wtf): wtf",
)
@patch("shutil.get_terminal_size")
@patch("wtf.command_output_loggers.screen_cmd_logger.ScreenCmdLogger._emulate_terminal")
def test_extract_command_outputs(mock_emulate_terminal, mock_get_terminal_size, mock_open, screen_cmd_logger):
    mock_get_terminal_size.return_value = MagicMock(columns=80)
    mock_emulate_terminal.side_effect = [
        [
            f"prompt${TERMINAL_PROMPT_END_MARKER}command",
            "command output",
            f"prompt${TERMINAL_PROMPT_END_MARKER} wtf",
        ]  # Emulated terminal data
    ]
    expected_output = [CommandOutput(output="command output")]
    assert screen_cmd_logger.extract_command_outputs() == expected_output
