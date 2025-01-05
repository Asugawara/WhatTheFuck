from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandOutput:
    output: str


@dataclass(frozen=True)
class CommandOutputLoggerBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def session_name(self) -> str:
        pass

    @abstractmethod
    def begin(self) -> None:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def extract_command_outputs(self) -> list[CommandOutput]:
        pass
