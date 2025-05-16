from abc import ABC, abstractmethod
from typing import TypeVar

UseCaseInput = TypeVar("UseCaseInput")
UseCaseOutput = TypeVar("UseCaseOutput")


class BaseUseCase(ABC):
    """Base case for Use Cases"""

    @abstractmethod
    def execute(self, uc_input: UseCaseInput) -> UseCaseOutput:
        """Main (and only one) required function to be called externally"""
