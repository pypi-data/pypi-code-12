import pytest
from datetime import timedelta
from sqlalchemy.sql import or_
from ..models import Entry
from ..resyndicators import Resyndicator


resyndicator1 = Resyndicator(
    title='Resyndicator 1',
    past=timedelta(days=365),
    query=or_(
        Entry.source_link.in_([
            'http://example.com/feed/atom/',
            'http://feeds.feedburner.com/TheGivewellBlog',
        ])
    )
)
resyndicator2 = Resyndicator(
    title='Resyndicator 2',
    past=timedelta(days=365),
    query=or_(
        Entry.source_link.in_([
            'http://example.com/feed/',
        ])
    )
)


@pytest.mark.parametrize('resyndicator,length', [
    (resyndicator1, 3),
    (resyndicator2, 0),
])
def test_get_entries(db, resyndicator, length):
    #import IPython; IPython.embed()
    assert len(resyndicator.get_entries()) == length


@pytest.mark.parametrize('resyndicator,length', [
    (resyndicator1, 3),
    (resyndicator2, 0),
])
def test_feed_entries(db, resyndicator, length):
    feed = resyndicator.feed
    print(feed)
    assert feed.count('<entry') == length
