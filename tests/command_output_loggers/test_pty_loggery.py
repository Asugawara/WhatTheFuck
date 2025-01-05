import hashlib
from unittest.mock import MagicMock, mock_open, patch

import pytest

from wtf.command_output_loggers.base import CommandOutput
from wtf.command_output_loggers.pty_logger import PtyLogger
from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER


@pytest.fixture
def pty_logger():
    return PtyLogger(logfile="test_logfile.log")


def test_session_name(pty_logger):
    expected_session_name = hashlib.sha256(b"test_logfile.log").hexdigest()
    assert pty_logger.session_name == expected_session_name


@patch("builtins.open", new_callable=mock_open)
@patch("pty.spawn")
def test_begin(mock_pty_spawn, mock_open, pty_logger):
    pty_logger.begin()
    mock_pty_spawn.assert_called_once()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=b"prompt$\ncommand output\nprompt$ wtf",
)
@patch("shutil.get_terminal_size")
@patch("wtf.command_output_loggers.pty_logger.PtyLogger._emulate_terminal")
def test_extract_command_outputs(mock_emulate_terminal, mock_get_terminal_size, mock_open, pty_logger):
    mock_get_terminal_size.return_value = MagicMock(columns=80)
    mock_emulate_terminal.side_effect = [
        [
            f"prompt${TERMINAL_PROMPT_END_MARKER}command",
            "command output",
            f"prompt${TERMINAL_PROMPT_END_MARKER} wtf",
        ]  # Emulated terminal data
    ]
    expected_output = [CommandOutput(output="command output")]
    assert pty_logger.extract_command_outputs() == expected_output
