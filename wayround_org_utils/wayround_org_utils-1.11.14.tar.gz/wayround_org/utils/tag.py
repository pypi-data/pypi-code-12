"""
Tag Utils
"""

import logging

import sqlalchemy.ext.declarative
import sqlalchemy.orm

import wayround_org.utils.terminal
import wayround_org.utils.db


class TagEngine(wayround_org.utils.db.BasicDB):

    def __init__(
            self,
            config_string=None,
            bind=None,
            decl_base=None,
            metadata=None,
            init_table_data='tag'
            ):

        super().__init__(
            config_string=config_string,
            bind=bind,
            decl_base=decl_base,
            metadata=metadata,
            init_table_data=init_table_data
            )

        return

    def init_table_mappings(self, init_table_data):

        class Tag(self.decl_base):

            __tablename__ = init_table_data

            tid = sqlalchemy.Column(
                sqlalchemy.Integer,
                primary_key=True,
                autoincrement=True
                )

            obj = sqlalchemy.Column(
                sqlalchemy.UnicodeText,
                nullable=False,
                default='',
                index=True
                )

            tag = sqlalchemy.Column(
                sqlalchemy.UnicodeText,
                nullable=False,
                default='',
                index=True
                )

        self.Tag = Tag

        return

    def get_mapped_tag_table(self):
        ret = None
        if self.Tag.__tablename__ in self.decl_base.metadata.tables:
            ret = self.decl_base.metadata.tables[self.Tag.__tablename__]
        return ret

    def create_tables(self):
        self.get_mapped_tag_table().create(checkfirst=True)
        return

    def set_many_objects_tags(
            self,
            obj_tags_2tuple_list,
            commit_every=1000
            ):
        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        commit_counter = 0

        for obj, tags in obj_tags_2tuple_list:

            if tags is None:
                tags = []

            session.query(self.Tag).filter_by(obj=obj).delete()

            for i in tags:
                a = self.Tag()
                a.obj = obj
                a.tag = i
                session.add(a)

            commit_counter += 1

            if commit_counter >= commit_every:
                logging.debug("Committing")
                session.commit()
                commit_counter = 0

        session.commit()
        session.close()

        return

    def set_object_tags(self, obj, tags=None):
        return self.set_many_objects_tags(
            [(obj, tags)]
            )

    def get_object_tags(self, obj):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        q = session.query(self.Tag).filter_by(obj=obj).all()

        ret = set()
        for i in q:
            ret.add(i.tag)

        session.close()

        return list(ret)

    def get_objects(self):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        q = session\
            .query(sqlalchemy.distinct(self.Tag.obj))\
            .order_by(self.Tag.obj)\
            .all()

        ret = list()

        for i in q:
            ret.append(i[0])

        session.close()

        return ret

    def get_objects_and_tags_dict(self):

        ret = dict()

        objs = self.get_objects()

        for i in objs:
            ret[i] = self.get_tags(i)

        return ret

    def get_all_tags(self):
        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        q = session.query(sqlalchemy.distinct(self.Tag.tag)).all()

        ret = []
        for i in q:
            ret.append(i[0])

        session.close()

        return ret

    def get_size(self):
        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        ret = session.query(self.Tag).count()

        session.close()

        return ret

    def get_objects_by_tag(self, tag):
        return self.get_objects_by_tags([tag])

    def get_objects_by_tags(self, tags):
        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        ret = set()

        q = session.query(self.Tag)\
            .filter(self.Tag.tag.in_(tags))\
            .all()

        for i in q:
            ret.add(i.obj)

        session.close()

        return list(ret)

    def del_object_tags(self, obj, synchronize_session='evaluate'):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        if isinstance(obj, list):

            if len(obj) > 0:
                for i in range(int(len(obj) / 100) + 1):
                    session.query(self.Tag)\
                        .filter(self.Tag.obj.in_(
                            obj[i * 100:(i + 1) * 100]
                            )
                        )\
                        .delete(
                            synchronize_session=synchronize_session
                            )

        else:
            session.query(self.Tag).filter_by(obj=obj).delete(
                synchronize_session=synchronize_session
                )

        session.commit()
        session.close()

        return

    def del_objects_by_tags(self, tags):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        session.query(self.Tag)\
            .filter(self.Tag.tag.in_(tags))\
            .delete()

        session.commit()
        session.close()

        return

    def remove_duplicated_objects(self, mute=True):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        logging.info("Loading...")
        objs = self.get_objects()
        logging.info("Cleaning...")

        changed = False
        ii = 0
        ic = len(objs)
        removed = 0
        for i in objs[:]:

            if objs.count(i) > 1:

                changed = True

                while i in objs:
                    objs.remove(i)

                removed += \
                    session.query(self.Tag)\
                    .filter_by(obj=i)\
                    .count()

                session.query(self.Tag)\
                    .filter_by(obj=i)\
                    .delete()

            ii += 1

            if not mute:
                wayround_org.utils.terminal.progress_write(
                    "    {} of {} ({:.2f}%, deleted {})".format(
                        ii,
                        ic,
                        100 / (float(ic / ii)),
                        removed
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        if changed:
            session.commit()

        session.close()

        return

    def clear(self):
        self.get_mapped_tag_table().delete()
        return
