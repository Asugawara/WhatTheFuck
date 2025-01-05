from typing import Literal

from wtf.command_output_loggers.base import CommandOutputLoggerBase
from wtf.command_output_loggers.pty_logger import PtyLogger
from wtf.command_output_loggers.script_cmd_logger import ScriptCmdLogger


def factroy_command_output_logger(
    logger_name: Literal["script", "pty"], logfile: str, terminal_prompt_lines: int
) -> CommandOutputLoggerBase:
    if logger_name == "script":
        return ScriptCmdLogger(logfile=logfile, terminal_prompt_lines=terminal_prompt_lines)
    elif logger_name == "pty":
        return PtyLogger(logfile=logfile, terminal_prompt_lines=terminal_prompt_lines)
    else:
        raise NotImplementedError("Only `script(Unix)` and `pty(Python built-in)` are supported")
