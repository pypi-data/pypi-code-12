from playhouse import shortcuts
from woodstove import hooks, db


@hooks.hook('route', 'exit')
def db_route_exit_hook(req):
    ''' Auto close connection at the end of request '''
    database = db.get_db(False)

    if not database.is_closed():
        database.close()

@hooks.hook('route', 'formatter')
def db_route_format_hook(req):
    ''' Convert db model to a dict for formatting '''
    if isinstance(req.ret, db.BaseModel):
        req.ret = shortcuts.model_to_dict(req.ret)
