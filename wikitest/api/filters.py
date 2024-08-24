from abc import ABC, abstractmethod
from typing import Iterator

from wikitest.api.model import Person


class PersonFilter(ABC):
    @abstractmethod
    def apply(self, person: Person) -> bool:
        pass


class ModernPersonFilter(PersonFilter):
    def apply(self, person: Person) -> bool:
        return person.birth_date is not None and person.death_date is None
