import os
from unittest.mock import call, mock_open, patch

import pytest

from wtf.shells.zsh import ZshShell


@pytest.fixture
def zsh_shell():
    return ZshShell()


@patch("shutil.copyfile")
@patch("os.path.exists", return_value=True)
def test_set_session(mock_exists, mock_copyfile, zsh_shell):
    zsh_shell.set_session("test_session")
    assert os.environ["HISTFILE"] == "/tmp/wtf/test_session_history"
    mock_copyfile.assert_called_with(os.path.expanduser("~/.zshrc"), "/tmp/wtf/.zshrc")


@patch("shutil.copyfile")
@patch("os.path.exists", return_value=False)
def test_set_session_no_zshrc(mock_exists, mock_copyfile, zsh_shell):
    zsh_shell.set_session("test_session")
    assert os.environ["HISTFILE"] == "/tmp/wtf/test_session_history"
    mock_copyfile.assert_called_with(os.path.expanduser("~/.zsh_history"), "/tmp/wtf/test_session_history")


@patch("builtins.open", new_callable=mock_open, read_data="echo 'hello'\nls\nwtf")
@patch("os.path.exists", return_value=True)
def test_get_session_histories(mock_exists, mock_file, zsh_shell):
    histories = zsh_shell.get_session_histories("test_session")
    assert histories == ["echo 'hello'", "ls"]


@patch("os.remove")
def test_restore(mock_remove, zsh_shell):
    zsh_shell.restore("test_session")
    calls = [call("/tmp/wtf/test_session_history"), call("/tmp/wtf/.zshrc")]
    mock_remove.assert_has_calls(calls)


@patch("os.getenv")
def test_get_terminal_prompt(mock_getenv, zsh_shell):
    mock_getenv.return_value = "prompt>"
    prompt = zsh_shell.get_terminal_prompt()
    assert prompt == "prompt>"
