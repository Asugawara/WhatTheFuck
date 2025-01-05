import os
import shutil
import subprocess
from dataclasses import dataclass
from textwrap import dedent

from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER
from wtf.shells.base import ShellBase


@dataclass(frozen=True)
class FishShell(ShellBase):
    HISTORY_FILE_CANDIDATES: tuple[str, ...] = (
        os.path.expanduser("~/.local/share/fish/fish_history"),
        os.path.expanduser("~/.config/fish/fish_history"),
    )
    CONFIG_FILE: str = os.path.expanduser("~/.config/fish/config.fish")
    TMP_CONFIG_DIR: str = "/tmp/wtf/"

    def _find_history_file(self) -> str:
        for candidate in self.HISTORY_FILE_CANDIDATES:
            if os.path.exists(candidate):
                return candidate
        raise FileNotFoundError("Fish history file not found")

    def set_session(self, session_name: str) -> None:
        os.environ["fish_history"] = session_name  # noqa
        # NOTE: a session history file is empty. copy the history file.
        head, tail = os.path.split(self._find_history_file())
        session_history_file = os.path.join(head, tail.replace("fish", session_name))
        shutil.copyfile(self._find_history_file(), session_history_file)
        shutil.copytree(
            os.path.dirname(self.CONFIG_FILE),
            os.path.join(self.TMP_CONFIG_DIR, "fish"),
            dirs_exist_ok=True,
        )
        os.environ["XDG_CONFIG_HOME"] = self.TMP_CONFIG_DIR

        with open(os.path.join(self.TMP_CONFIG_DIR, "fish", "config.fish"), "a") as f:
            f.write(
                dedent(
                    f"""
            functions -c fish_prompt _original_fish_prompt
            function fish_prompt
                _original_fish_prompt
                printf '{TERMINAL_PROMPT_END_MARKER}'
            end
            """
                )
            )

    def get_session_histories(self, session_name: str) -> list[str]:
        histories = []
        head, tail = os.path.split(self._find_history_file())
        session_history_file = os.path.join(head, tail.replace("fish", session_name))
        with open(session_history_file) as f:
            for line in f.readlines():
                if "- cmd:" in line:
                    histories.append(line.split("- cmd:", 1)[1].strip())
        return histories[:-1]  # Exclude self command

    def restore(self, session_name: str) -> None:
        head, tail = os.path.split(self._find_history_file())
        session_history_file = os.path.join(head, tail.replace("fish", session_name))
        if os.path.exists(session_history_file):
            os.remove(session_history_file)
        shutil.rmtree(os.path.join(self.TMP_CONFIG_DIR, "fish"))

    def get_terminal_prompt(self) -> str:
        fish_prompt = subprocess.run([os.getenv("SHELL", "fish"), "-c", "fish_prompt"], capture_output=True)
        return fish_prompt.stdout.decode().strip()
