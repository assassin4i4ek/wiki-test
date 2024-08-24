from typing import Any, Sequence

from elasticsearch import Elasticsearch

from wikitest.api.model import Person, PersonSearchQuery
from wikitest.api.datasets import PersonDataset


class PersonElasticDb:
    def __init__(self):
        self._es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
        self._index_name = 'persons'

    def insert(self, dataset: PersonDataset):
        if not self._es.indices.exists(index=self._index_name):
            self._create_index()

        for person in dataset:
            person_dict = self._person_to_dict(person)
            res = self._es.index(index=self._index_name, document=person_dict)

    def search(self, query: PersonSearchQuery) -> Sequence[Person]:
        query.validate()
        body = self._person_query_to_dict(query)
        res = self._es.search(index=self._index_name, body=body)
        matches = res['hits']['hits']
        # Print the results
        persons = [
            self._person_from_dict(match['_source'])
            for match in matches
        ]
        return persons

    def clear(self):
        if self._es.indices.exists(index=self._index_name):
            self._es.indices.delete(index=self._index_name)

    def _create_index(self):
        index_body = {
            'mappings': {
                'properties': {
                    'name': {
                        'type': 'keyword'
                    },
                    'surname': {
                        'type': 'keyword'
                    },
                    'patronymic': {
                        'type': 'keyword'
                    },
                    'birth_date': {
                        'type': 'text'
                        # 'type': 'date',
                        # 'format': 'yyyy-MM-dd'
                    },
                    'death_date': {
                        'type': 'text'
                        # 'type': 'date',
                        # 'format': 'yyyy-MM-dd'
                    },
                    'src_article': {
                        'type': 'text'
                    }
                }
            }
        }
        self._es.indices.create(index=self._index_name, body=index_body)

    @staticmethod
    def _person_to_dict(person: Person) -> dict[str, Any]:
        person_dict = {
            'name': person.name,
            'surname': person.surname,
            'patronymic': person.patronymic,
            'birth_date': person.birth_date,
            'death_date': person.death_date,
            'src_article': person.src_article,
        }
        return person_dict

    @staticmethod
    def _person_from_dict(person_dict: dict[str, Any]) -> Person:
        return Person(
            name=person_dict['name'],
            surname=person_dict['surname'],
            patronymic=person_dict['patronymic'],
            birth_date=person_dict['birth_date'],
            death_date=person_dict['death_date'],
            src_article=person_dict['src_article'],
        )

    @staticmethod
    def _person_query_to_dict(query: PersonSearchQuery) -> dict[str, Any]:
        matches = []
        if query.name:
            matches.append({
                'wildcard': {
                    'name': f'*{query.name}*'
                }
            })
        if query.surname:
            matches.append({
                'wildcard': {
                    'surname': f'*{query.surname}*'
                }
            })
        if query.patronymic:
            matches.append({
                'wildcard': {
                    'patronymic': f'*{query.patronymic}*'
                }
            })
        # if query.birth_date:
        #     matches.append({
        #         'match': {
        #             'birth_date': query.birth_date
        #         }
        #     })
        # if query.death_date:
        #     matches.append({
        #         'match': {
        #             'death_date': query.death_date
        #         }
        #     })
        assert len(matches) > 0
        body = {
            'query': {
                'bool': {
                    'should': matches
                }
            }
        }
        return body
