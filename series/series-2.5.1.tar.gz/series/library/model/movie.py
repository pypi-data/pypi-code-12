import functools

from series.db import Database, Column, String, Boolean


@functools.total_ordering
class Movie(object, metaclass=Database.DefaultMeta):
    title = Column(String)
    removed = Column(Boolean)
    subfps = Column(String)
    new = Column(Boolean)

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Movie {}>'.format(self.formatted_title)

    def __lt__(self, other):
        if isinstance(other, Movie):
            return self.title < other.title

    def __eq__(self, other):
        if isinstance(other, Movie):
            return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    @property
    def info(self):
        return dict(
            title=self.title,
            new=self.new,
            type='movie',
        )

    @property
    def subfps_fallback(self):
        return self.subfps

    @property
    def formatted_title(self):
        return self.title.replace('_', ' ').title()

    @property
    def resume_position(self):
        pass

__all__ = ['Movie']
