from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    """

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]: ...
