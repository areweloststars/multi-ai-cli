from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def ask(self, prompt: str) -> str: ...
