import os

from wtf.shells.base import ShellBase
from wtf.shells.bash import BashShell
from wtf.shells.fish import FishShell


def factroy_shell() -> ShellBase:
    shell_path = os.getenv("SHELL", "")
    if shell_path.endswith("bash"):
        return BashShell()
    if shell_path.endswith("fish"):
        return FishShell()
    raise NotImplementedError("Only `bash` or `fish` shell are supported")
