import hashlib
from unittest.mock import patch, mock_open, MagicMock

import pytest

from wtf.command_output_loggers.base import CommandOutput
from wtf.command_output_loggers.tmux_cmd_logger import TmuxCmdLogger
from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER


@pytest.fixture
def tmux_cmd_logger():
    return TmuxCmdLogger(logfile="test_logfile.log")


def test_session_name(tmux_cmd_logger):
    expected_session_name = hashlib.sha256("test_logfile.log".encode()).hexdigest()
    assert tmux_cmd_logger.session_name == expected_session_name


@patch("subprocess.run")
def test_begin(mock_subprocess_run, tmux_cmd_logger):
    tmux_cmd_logger.begin()
    mock_subprocess_run.assert_any_call(["tmux", "new", "-d", "-s", tmux_cmd_logger.session_name])
    mock_subprocess_run.assert_any_call(
        ["tmux", "pipe-pane", "-O", "-t", tmux_cmd_logger.session_name, f"cat >> {tmux_cmd_logger.logfile}"]
    )
    mock_subprocess_run.assert_any_call(["tmux", "attach", "-t", tmux_cmd_logger.session_name])
    mock_subprocess_run.assert_any_call(["tmux", "kill-session", "-t", tmux_cmd_logger.session_name])


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=b"prompt$(wtf): command\ncommand output\nprompt$(wtf): wtf",
)
@patch("shutil.get_terminal_size")
@patch("wtf.command_output_loggers.tmux_cmd_logger.TmuxCmdLogger._emulate_terminal")
def test_extract_command_outputs(mock_emulate_terminal, mock_get_terminal_size, mock_open, tmux_cmd_logger):
    mock_get_terminal_size.return_value = MagicMock(columns=80)
    mock_emulate_terminal.side_effect = [
        [
            f"prompt${TERMINAL_PROMPT_END_MARKER}command",
            "command output",
            f"prompt${TERMINAL_PROMPT_END_MARKER} wtf",
        ]  # Emulated terminal data
    ]
    expected_output = [CommandOutput(output="command output")]
    assert tmux_cmd_logger.extract_command_outputs() == expected_output
