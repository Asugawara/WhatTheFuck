import os
import shutil
from dataclasses import dataclass

from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER
from wtf.shells.base import ShellBase


@dataclass(frozen=True)
class BashShell(ShellBase):
    HISTFILE_TEMPLATE = "/tmp/wtf/{session_name}_history"

    def set_session(self, session_name: str) -> None:
        histfile = self.HISTFILE_TEMPLATE.format(session_name=session_name)
        os.environ["HISTFILE"] = histfile
        # NOTE: for real-time history saving
        os.environ["PROMPT_COMMAND"] = f"history -w; {os.getenv('PROMPT_COMMAND', '')}"
        shutil.copyfile(os.path.expanduser("~/.bash_history"), histfile)

        os.environ["PS1"] = f"{os.getenv('PS1', '')}{TERMINAL_PROMPT_END_MARKER}"

    def get_session_histories(self, session_name: str) -> list[str]:
        with open(self.HISTFILE_TEMPLATE.format(session_name=session_name)) as f:
            histories = [line.strip() for line in f.readlines()]
        return histories

    def restore(self, session_name: str) -> None:
        os.remove(self.HISTFILE_TEMPLATE.format(session_name=session_name))

    def get_terminal_prompt(self) -> str:
        return os.getenv("PS1", "")
