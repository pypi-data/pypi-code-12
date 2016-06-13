from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem, BaseFactory
from ringo.model.mixins import Owned


class FileFactory(BaseFactory):

    def create(self, user=None, values=None):
        new_item = BaseFactory.create(self, user, values)
        return new_item


class File(BaseItem, Owned, Base):
    """Docstring for file extension"""

    __tablename__ = 'files'
    """Name of the table in the database for this modul. Do not
    change!"""
    _modul_id = None
    """Will be set dynamically. See include me of this modul"""

    # Define columns of the table in the database
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.Text, nullable=True, default=None)
    data = sa.Column('data', sa.LargeBinary, nullable=True, default=None)
    description = sa.Column('description', sa.Text,
                            nullable=True, default=None)
    size = sa.Column('size', sa.Integer, nullable=True, default=None)
    mime = sa.Column('mime', sa.Text, nullable=True, default=None)

    @classmethod
    def get_item_factory(cls):
        return FileFactory(cls)


class Filed(object):
    """Mixin to make items of other modules fileable. This means the
    will get a relation named files linked to files attached to the item."""

    @declared_attr
    def files(cls):
        clsname = cls.__name__.lower()
        tbl_name = "nm_%s_files" % clsname
        nm_table = sa.Table(tbl_name, Base.metadata,
                            sa.Column('%s_id' % clsname, sa.Integer,
                                      sa.ForeignKey(cls.id)),
                            sa.Column('file_id', sa.Integer,
                                      sa.ForeignKey("files.id")))
        files = sa.orm.relationship(File, secondary=nm_table,
                                    single_parent=True,
                                    backref="items")
        return files


# Delete orphaned files. See details on:
# http://stackoverflow.com/questions/9234082/setting-delete-orphan-on-sqlalchemy-relationship-causes-assertionerror-this-att
# after_flush did not work so clean up right before the commit.
@sa.event.listens_for(sa.orm.Session, 'before_commit')
def delete_tag_orphans(session):
        session.query(File).\
        filter(~File.items.any()).\
        delete(synchronize_session=False)
