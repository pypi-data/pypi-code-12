"""
A better version of oic.utils.sdb:SessionDB.

The real one is not designed to afford for sessions shared between multiple
processes/hosts, because it uses an in-memory cache of .uid2sid to find sessions
for a given user.
By Benjamin Goering
"""
from future.moves import itertools

from oic.utils.sdb import SessionDB as OICSessionDB

from collections import Mapping
import logging

LOG = logging.getLogger(__name__)


def uid_from_session(session):
    return session['authn_event'].uid


class SessionStorageUid2Sid(Mapping):
    """
    Implement object required by oic.oic.provider:Provider.uid2sid,
    except it's not just a dict. It's a Mapping that reads from a Mapping
    of Session IDs (sids) to Sessions (as created by
    oic.oic.provider:Provider.create_authz_session)
    https://github.com/rohe/pyoidc/issues/146
    """

    def __init__(self, sessions_by_id, uid_from_session=uid_from_session):
        self._sessions_by_id = sessions_by_id
        self._uid_from_session = uid_from_session

    def __getitem__(self, uid):
        session_items_for_uid = itertools.ifilter(
            lambda i: uid == self._uid_from_session(i[1]),
            self._sessions_by_id.items())
        # Would be neat if oic.utils.sdb explicitly cast to list() bcuz lazy
        return list(sid for (sid, session) in session_items_for_uid)

    def __iter__(self):
        sessions_sorted_by_uuid = sorted(self._sessions_by_id.values(),
                                         key=self._uid_from_session)
        for uid, user_sessions in itertools.groupby(sessions_sorted_by_uuid,
                                                    self._uid_from_session):
            yield uid

    def __len__(self):
        return len(iter(self))


def create_uid2sid_from_db(sessions_by_id):
    """
    :param db: `db` like that passed to SessionDB constructor
    :returns: Object that reads from db to provide a usable uid2sid map,
      which currently means:
      try:
          self.uid2sid[uid].append(sid)
      except KeyError:
          self.uid2sid[uid] = [sid]
      self.uid2sid.items()
      self.uid2sid.values()
      self.uid2sid[sid] = sid
    """
    LOG.debug('create_uid2sid_from_db %s', sessions_by_id)
    return SessionStorageUid2Sid(sessions_by_id)


class SessionDB(OICSessionDB):

    def __init__(self, *args, **kwargs):
        """
        :param uid2sid: Mapping of UID to session IDs
        """
        uid2sid = kwargs.pop('uid2sid', None)
        super(SessionDB, self).__init__(*args, **kwargs)
        # https://github.com/rohe/pyoidc/pull/147
        kwarg_db = kwargs.get('db')
        if kwarg_db is not None:
            self._db = kwarg_db
        self.uid2sid = uid2sid or create_uid2sid_from_db(self._db)

    def __delitem__(self, sid):
        # Exactly like super(), except don't re-assing .uid2sid
        del self._db[sid]
