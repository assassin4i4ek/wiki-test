from abc import ABC, abstractmethod
from typing import Iterator

from wikitest.api.model import Person


class PersonDataset(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[Person]:
        pass
