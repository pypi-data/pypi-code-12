import datetime
import pytest
from .. import settings

settings.DATABASE = 'sqlite://'
settings.BASE_URL = 'http://example.com/'

from ..models import Base, engine, Session, Entry


@pytest.fixture(scope='module')
def db(request):
    year = datetime.date.today().year
    session = Session()
    session.add(
        Entry(
            id='http://example.com/mock-title-1',
            updated=datetime.datetime(year, 5, 17, 0, 0, 10),
            published=datetime.datetime(year, 5, 17, 0, 0, 0),
            title='Mock Title 1',
            author='Mock Author 1',
            link='http://example.com/mock-title-1',
            summary='Mock summary 1',
            summary_type='text',
            content='<p>Mock content 1</p>',
            content_type='html',
            source_id='http://example.com/feed/atom/',
            source_title='Mock Source 1',
            source_link='http://example.com/feed/atom/'))
    session.add(
        Entry(
            id='http://example.com/mock-title-2',
            updated=datetime.datetime(year, 5, 18, 0, 0, 10),
            published=datetime.datetime(year, 5, 18, 0, 0, 0),
            title='Mock Title 2',
            author='Mock Author 2',
            link='http://example.com/mock-title-2',
            summary='<p>Mock summary 2</p>',
            summary_type='html',
            content='<p>Mock content 2</p>',
            content_type='html',
            source_id='http://example.com/feed/atom/',
            source_title='Mock Source 2',
            source_link='http://example.com/feed/atom/'))
    session.add(
        Entry(
            id='http://example.com/mock-title-3',
            updated=datetime.datetime(year, 5, 19, 0, 0, 10),
            published=datetime.datetime(year, 5, 19, 0, 0, 0),
            title='Mock Title 3',
            author='Mock Author 3',
            link='http://example.com/mock-title-3',
            summary='Mock summary 3',
            summary_type='text',
            content='<p>Mock content 3</p>',
            content_type='html',
            source_id='http://example.com/feed/atom/',
            source_title='Mock Source 3',
            source_link='http://example.com/feed/atom/'))
    session.commit()
    def fin():
        session.query(Entry).filter_by(
            source_id='http://example.com/feed/atom/').delete()
    request.addfinalizer(fin)
    return session
