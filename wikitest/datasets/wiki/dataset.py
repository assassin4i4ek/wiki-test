from typing import Any, Iterator, Optional

from lxml import etree
from tqdm import tqdm

from wikitest.api.datasets import PersonDataset
from wikitest.api.model import Person
from wikitest.api.filters import PersonFilter
from wikitest.datasets.wiki.parser import PersonPageParser


class TestDataset(PersonDataset):
    def __iter__(self) -> Iterator[Person]:
        persons = [
            Person(name='Шевченко Олександр Петрович', surname=None, patronymic=None,
                   birth_date=None, death_date=None),
            Person(name='Шевчук Петро Олексійович', surname=None, patronymic=None,
                   birth_date=None, death_date=None),
        ]
        for person in persons:
            yield person


class MediaWikiDataset(PersonDataset):
    def __init__(self, path: str, take_n: Optional[int] = -1):
        self.path = path
        self.take_n = take_n
        self._parser = PersonPageParser()
        self._filters: list[PersonFilter] = []
    
    def __iter__(self) -> Iterator[Person]:
        counter = 0
        pages_iter = etree.iterparse(self.path, tag='{*}page')

        for _, page_elem in tqdm(pages_iter):
            # filter redirects
            if not self._filter_page(page_elem):
                page_elem.clear()
                continue
            # fetch tilte & text
            revis = self._get_child(page_elem, 'revision')
            assert revis is not None
            page_title_elem = self._get_child(page_elem, 'title')
            page_text_elem = self._get_child(revis, 'text')
            assert page_text_elem is not None
            page_title = page_title_elem.text
            page_text = page_text_elem.text
            # clean element
            page_elem.clear()
            person = self._parser.try_parse(page_title, page_text)
            if person is None:
                continue
            if not self._apply_person_filters(person):
                continue
            yield person
            counter += 1
            if counter == self.take_n:
                break

    def add_filter(self, filt: PersonFilter):
        self._filters.append(filt)

    def _ext_ns(self, tag: str, ns: Optional[str]) -> str:
        if ns:
            return f'{{{ns}}}{tag}'
        else:
            return tag

    def _filter_page(self, page: Any) -> bool:
        ns = page.nsmap.get(None)
        has_redirect = self._ext_ns('redirect', ns) in (child.tag for child in page)
        return not has_redirect

    def _get_child(self, elem: Any, tag: str) -> Any:
        ns = elem.nsmap.get(None)
        return elem.find(self._ext_ns(tag, ns))

    def _apply_person_filters(self, person: Person) -> bool:
        filters = (filt.apply(person) for filt in self._filters)
        return all(filters)
