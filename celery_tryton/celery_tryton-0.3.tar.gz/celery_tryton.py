# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Cédric Krier
# Copyright (c) 2013-2016, B2CK
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from celery import Task, Celery

try:
    from trytond import __version__ as trytond_version
except ImportError:
    from trytond.version import VERSION as trytond_version
trytond_version = tuple(map(int, trytond_version.split('.')))
try:
    from trytond.config import config
except ImportError:
    from trytond.config import CONFIG as config
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond import backend

__version__ = '0.3'
__all__ = ['TrytonTask', 'celery_app']


class TrytonTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        database = kwargs.pop('_database', self.app.conf.TRYTON_DATABASE)
        user = kwargs.pop('_user', 0)
        context = kwargs.pop('_context', {})

        if self.app.conf.CELERY_ALWAYS_EAGER:
            return super(TrytonTask, self).__call__(*args, **kwargs)

        config_file = self.app.conf.get('TRYTON_CONFIG', None)
        config.update_etc(config_file)
        # 3.0 compatibility
        if hasattr(config, 'set_timezone'):
            config.set_timezone()

        DatabaseOperationalError = backend.get('DatabaseOperationalError')
        if database not in Pool.database_list():
            with Transaction().start(database, 0, readonly=True):
                Pool(database).init()

        if trytond_version >= (3, 3):
            with Transaction().start(database, 0):
                Cache.clean(database)
            retry = config.getint('database', 'retry')
        else:
            Cache.clean(database)
            retry = int(config['retry'])
        with Transaction().start(
                database, user, context=context) as transaction:
            try:
                result = super(TrytonTask, self).__call__(*args, **kwargs)
                if hasattr(transaction, 'cursor'):
                    transaction.cursor.commit()
            except DatabaseOperationalError, exc:
                if hasattr(transaction, 'cursor'):
                    transaction.cursor.rollback()
                raise self.retry(args=args, kwargs=kwargs, exc=exc,
                    countdown=0, max_retries=retry)
            if trytond_version >= (3, 3):
                Cache.resets(database)
        if trytond_version < (3, 3):
            Cache.resets(database)
        return result

    def apply_async(self, args=None, kwargs=None, *a, **k):
        kwargs = _add_transaction(kwargs)
        return super(TrytonTask, self).apply_async(
            args=args, kwargs=kwargs, *a, **k)

    def subtask(self, *args, **kwargs):
        kwargs = _add_transaction(kwargs)
        return super(TrytonTask, self).subtask(*args, **kwargs)


def _add_transaction(kwargs):
    transaction = Transaction()
    if transaction.database:
        kwargs = kwargs.copy()
        kwargs['_database'] = transaction.database.database_name
        kwargs['_user'] = transaction.user
        kwargs['_context'] = transaction.context
    return kwargs


celery_app = Celery('tryton')
celery_app.config_from_object(
    config.get('celery', 'config'), silent=True)
