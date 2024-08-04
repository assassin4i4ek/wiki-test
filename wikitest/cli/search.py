import sys
from pprint import pprint

from wikitest.api.db import PersonElasticDb
from wikitest.api.model import PersonSearchQuery


if __name__ == '__main__':
    db = PersonElasticDb()
    assert len(sys.argv) > 1
    pattern = sys.argv[1]
    query = PersonSearchQuery(
        name=pattern,
        surname=pattern,
        patronymic=pattern,
        birth_date=pattern,
        death_date=pattern
    )
    res = db.search(query)
    pprint(res)
