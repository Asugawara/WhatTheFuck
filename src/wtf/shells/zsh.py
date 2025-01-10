import os
import shutil
from dataclasses import dataclass

from wtf.constants.constants import TERMINAL_PROMPT_END_MARKER
from wtf.shells.base import ShellBase


# WIP
@dataclass(frozen=True)
class ZshShell(ShellBase):
    HISTFILE_TEMPLATE: str = "/tmp/wtf/{session_name}_history"
    TMP_CONFIG_DIR: str = "/tmp/wtf"

    def set_session(self, session_name: str) -> None:
        histfile = self.HISTFILE_TEMPLATE.format(session_name=session_name)
        os.makedirs(os.path.dirname(histfile), exist_ok=True)
        shutil.copyfile(os.path.expanduser("~/.zsh_history"), histfile)
        tmp_zshrc = os.path.join(self.TMP_CONFIG_DIR, ".zshrc")
        original_zshrc = os.path.expanduser("~/.zshrc")
        if os.path.exists(original_zshrc):
            shutil.copyfile(original_zshrc, tmp_zshrc)
        with open(tmp_zshrc, "a") as f:
            f.write(f"HISTFILE={histfile}\n")
            f.write("setopt INC_APPEND_HISTORY\n")
            f.write("PS1=${PS1-}${TERMINAL_PROMPT_END_MARKER}\n")
        os.environ["TERMINAL_PROMPT_END_MARKER"] = TERMINAL_PROMPT_END_MARKER
        os.environ["ZDOTDIR"] = self.TMP_CONFIG_DIR

    def get_session_histories(self, session_name: str) -> list[str]:
        with open(self.HISTFILE_TEMPLATE.format(session_name=session_name)) as f:
            histories = [line.strip() for line in f.readlines()]
        return histories[:-1]  # Exclude self command

    def restore(self, session_name: str) -> None:
        os.remove(self.HISTFILE_TEMPLATE.format(session_name=session_name))
        os.remove(os.path.join(self.TMP_CONFIG_DIR, ".zshrc"))

    def get_terminal_prompt(self) -> str:
        return os.getenv("PS1", "")
