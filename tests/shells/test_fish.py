import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from wtf.shells.fish import FishShell


@pytest.fixture
def fish_shell():
    return FishShell()


@patch("os.path.exists")
def test_find_history_file_exists(mock_exists, fish_shell):
    mock_exists.side_effect = [True]
    assert fish_shell._find_history_file() == os.path.expanduser("~/.local/share/fish/fish_history")


@patch("os.path.exists")
def test_find_history_file_exists2(mock_exists, fish_shell):
    mock_exists.side_effect = [False, True]
    assert fish_shell._find_history_file() == os.path.expanduser("~/.config/fish/fish_history")


@patch("os.path.exists", return_value=False)
def test_find_history_file_not_found(mock_exists, fish_shell):
    with pytest.raises(FileNotFoundError):
        fish_shell._find_history_file()


@patch("builtins.open", new_callable=mock_open)
@patch("shutil.copytree")
@patch("os.environ", {})
@patch("shutil.copyfile")
@patch("os.path.exists", return_value=True)
def test_set_session(mock_exists, mock_copyfile, mock_copytree, mock_open, fish_shell):
    fish_shell.set_session("test_session")
    assert os.environ["fish_history"] == "test_session"
    mock_copyfile.assert_called_once()
    mock_copytree.assert_called_once()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="- cmd:echo 'hello'\n- cmd:ls\n- cmd: wtf",
)
@patch("os.path.exists", return_value=True)
def test_get_session_histories(mock_exists, mock_file, fish_shell):
    histories = fish_shell.get_session_histories("test_session")
    assert histories == ["echo 'hello'", "ls"]


@patch("shutil.rmtree")
@patch("os.path.exists", return_value=True)
@patch("os.remove")
def test_restore(mock_remove, mock_exists, mock_rmtree, fish_shell):
    fish_shell.restore("test_session")
    mock_remove.assert_called_once()
    mock_rmtree.assert_called_once()


@patch("subprocess.run")
def test_get_terminal_prompt(mock_run, fish_shell):
    mock_run.return_value = MagicMock(stdout=b"prompt>")
    prompt = fish_shell.get_terminal_prompt()
    assert prompt == "prompt>"
