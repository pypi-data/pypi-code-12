from sqlalchemy import event
from ..model import db


def increase(connection, table, item_id, column, step=1):
    values = {column: getattr(table.c, column) + step}
    stmt = table.update() \
        .where(table.c.id == item_id) \
        .values(**values)
    connection.execute(stmt)


def listen_increase(listen_table, update_table, target_id, column, step=1):

    if not update_table.has_property(column):
        return

    @event.listens_for(listen_table, 'after_insert')
    def item_after_create(mapper, connection, target):
        increase(connection, update_table.__table__, getattr(target, target_id), column, step)

    @event.listens_for(listen_table, 'before_delete')
    def item_before_delete(mapper, connection, target):
        increase(connection, update_table.__table__, getattr(target, target_id), column, -step)

    if listen_table.has_property('deleted'):
        @event.listens_for(listen_table.deleted, 'set')
        def item_deleted_set(target, value, oldvalue, initiator):
            if value and value != oldvalue:
                increase(db.session, update_table.__table__, getattr(target, target_id), column, -step)

            elif not value and value != oldvalue:
                increase(db.session, update_table.__table__, getattr(target, target_id), column, step)
