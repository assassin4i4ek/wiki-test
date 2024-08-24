import sys

from wikitest.api.db import PersonElasticDb
from wikitest.api.filters import ModernPersonFilter
from wikitest.datasets.wiki.dataset import MediaWikiDataset, TestDataset


if __name__ == '__main__':
    assert len(sys.argv) > 1
    db = PersonElasticDb()
    filters = [
        ModernPersonFilter(),
    ]
    for data_path in sys.argv[1:]: 
        # data = TestDataset()
        print(f'Processing data {data_path}')
        data = MediaWikiDataset(data_path)
        for filt in filters:
            data.add_filter(filt)
        db.insert(data)
