import os
from unittest.mock import mock_open, patch

import pytest

from wtf.shells.bash import BashShell


@pytest.fixture
def bash_shell():
    return BashShell()


@patch("shutil.copyfile")
@patch("os.path.exists", return_value=True)
def test_set_session(mock_exists, mock_copyfile, bash_shell):
    bash_shell.set_session("test_session")
    assert os.environ["HISTFILE"] == "/tmp/wtf/test_session_history"
    mock_copyfile.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data="echo 'hello'\nls")
@patch("os.path.exists", return_value=True)
def test_get_session_histories(mock_exists, mock_file, bash_shell):
    histories = bash_shell.get_session_histories("test_session")
    assert histories == ["echo 'hello'", "ls"]


@patch("os.path.exists", return_value=True)
@patch("os.remove")
def test_restore(mock_remove, mock_exists, bash_shell):
    bash_shell.restore("test_session")
    mock_remove.assert_called_once()


@patch("os.getenv")
def test_get_terminal_prompt(mock_getenv, bash_shell):
    mock_getenv.return_value = "prompt>"
    prompt = bash_shell.get_terminal_prompt()
    assert prompt == "prompt>"
