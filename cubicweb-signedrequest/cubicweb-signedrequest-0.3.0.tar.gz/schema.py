# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-signedrequest schema"""

try:
    from cubicweb import _
except ImportError:
    _ = unicode

from yams.buildobjs import String, Boolean, RelationDefinition, EntityType
from cubicweb.schema import (ERQLExpression, RRQLExpression,
                             RQLVocabularyConstraint)


class AuthToken(EntityType):
    """Authentication token"""
    __permissions__ = {'read': ('managers', ERQLExpression('X token_for_user U')),
                       'update': (ERQLExpression('X token_for_user U'),),
                       'add': ('managers', ERQLExpression('X token_for_user U')),
                       'delete': ('managers', ERQLExpression('X token_for_user U'))}
    enabled = Boolean(required=True, default=False)
    token = String(maxsize=128, required=True, description=_(u'secret token'),
                   # use default 'read' permission as RQL expressions are not
                   # allowed in 'read' permission but rely on entity type
                   # permissions anyways.
                   __permissions__={'read': ('managers', 'users', 'guests',),
                                    'add': (),
                                    'update': ()},
                  )
    id = String(maxsize=128, required=True, unique=True,
                description=_(u'identifier for the token (must be unique)'))


class token_for_user(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests',),
                       'delete': ('managers', RRQLExpression('S token_for_user U')),
                       'add': ('managers', 'users'),
                      }
    subject = 'AuthToken'
    object = 'CWUser'
    cardinality = '1*'
    inlined = True
    composite = 'object'
