from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class Person:
    name: str
    surname: Optional[str]
    patronymic: Optional[str]
    birth_date: Optional[str]
    death_date: Optional[str]
    src_article: str


@dataclass
class PersonSearchQuery:
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None

    def validate(self):
        is_empty = self._is_empty()
        if is_empty:
            raise ValueError(f'{self} is empty')

    def _is_empty(self) -> bool:
        if self.name:
            return False
        if self.surname:
            return False
        if self.patronymic:
            return False
        if self.birth_date:
            return False
        if self.death_date:
            return False
        return True
