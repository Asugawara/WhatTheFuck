import hashlib
from unittest.mock import MagicMock, mock_open, patch

import pytest

from wtf.command_output_loggers.base import CommandOutput
from wtf.command_output_loggers.script_cmd_logger import ScriptCmdLogger
from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER


@pytest.fixture
def script_cmd_logger():
    return ScriptCmdLogger(logfile="test_logfile.log")


def test_session_name(script_cmd_logger):
    expected_session_name = hashlib.sha256(b"test_logfile.log").hexdigest()
    assert script_cmd_logger.session_name == expected_session_name


@patch("subprocess.run")
def test_begin(mock_subprocess_run, script_cmd_logger):
    script_cmd_logger.begin()
    mock_subprocess_run.assert_called_once_with(["script", "-q", "-F", "test_logfile.log"])


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=b"prompt$(wtf): command\ncommand output\nprompt$(wtf): wtf",
)
@patch("shutil.get_terminal_size")
@patch("wtf.command_output_loggers.script_cmd_logger.ScriptCmdLogger._emulate_terminal")
def test_extract_command_outputs(mock_emulate_terminal, mock_get_terminal_size, mock_open, script_cmd_logger):
    mock_get_terminal_size.return_value = MagicMock(columns=80)
    mock_emulate_terminal.side_effect = [
        [
            f"prompt${TERMINAL_PROMPT_END_MARKER}command",
            "command output",
            f"prompt${TERMINAL_PROMPT_END_MARKER} wtf",
        ]  # Emulated terminal data
    ]
    expected_output = [CommandOutput(output="command output")]
    assert script_cmd_logger.extract_command_outputs() == expected_output
