import os

from wtf.shells.base import ShellBase
from wtf.shells.bash import BashShell
from wtf.shells.fish import FishShell
from wtf.shells.zsh import ZshShell


def factroy_shell() -> ShellBase:
    shell_path = os.getenv("SHELL", "")
    if shell_path.endswith("bash"):
        return BashShell()
    if shell_path.endswith("fish"):
        return FishShell()
    if shell_path.endswith("zsh"):
        return ZshShell()
    raise NotImplementedError("Only `bash` or `fish` shell are supported")
