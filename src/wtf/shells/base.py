from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ShellBase(metaclass=ABCMeta):
    @abstractmethod
    def set_session(self, session_name: str) -> None:
        pass

    @abstractmethod
    def get_session_histories(self, session_name: str) -> list[str]:
        pass

    @abstractmethod
    def restore(self, session_name: str) -> None:
        pass

    @abstractmethod
    def get_terminal_prompt(self) -> str:
        pass
