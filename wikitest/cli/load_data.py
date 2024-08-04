import sys

from wikitest.api.db import PersonElasticDb
from wikitest.datasets.wiki.dataset import MediaWikiDataset, TestDataset


if __name__ == '__main__':
    assert len(sys.argv) > 1
    db = PersonElasticDb()
    for data_path in sys.argv[1:]: 
        # data = TestDataset()
        data = MediaWikiDataset(data_path)
        db.insert(data)
