# encoding: utf8
#
# This file is part of the Neurons project.
# Copyright (c), Arskom Ltd. (arskom.com.tr),
#                Burak Arslan <burak.arslan@arskom.com.tr>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Arskom Ltd. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from spyne import rpc, Integer64, Iterable, Mandatory as M
from spyne.util import memoize
from spyne.error import ResourceNotFoundError
from spyne.protocol.http import HttpPattern

from neurons.base.dal import DalBase
from neurons.base.service import TReaderServiceBase, TWriterServiceBase


@memoize
def TCrudServices(T, T_name=None, _LogEntry=None):
    if T_name is None:
        T_name = T.__name__


    class Dal(DalBase):
        def get_all(self):
            def _cb(stream):
                for t in self.session.query(T).order_by(T.id).yield_per(1000):
                    stream.write(t)
            return Iterable.Push(_cb)

        def get(self, id):
            return self.session.query(T).filter_by(id=id).one()

        def put(self, obj):
            if obj.id is None:
                self.session.add(obj)
                self.session.flush() # so that we get the obj.id value

            else:
                if self.session.query(T).get(obj.id) is None:
                    # this is to prevent the client from setting the primary key
                    # of a new object instead of the database's own primary-key
                    # generator.
                    raise ResourceNotFoundError('%s.id=%d' % (T_name, obj.id))

                else:
                    self.session.merge(obj)

            return obj.id


    class ReadService(TReaderServiceBase(_LogEntry)):
        @rpc(_returns=Iterable(T), _patterns=[HttpPattern('/list')])
        def get_all(ctx):
            return Dal(ctx).get_all()

        @rpc(M(Integer64), _returns=T, _patterns=[HttpPattern('/<id>', verb='GET')])
        def get(ctx, id):
            return Dal(ctx).get(id)

        @rpc(_returns=T)
        def new(ctx):
            return T()


    class WriteService(TWriterServiceBase(_LogEntry)):
        @rpc(T, _returns=T, _patterns=[HttpPattern('/put', verb='(PUT|POST)')],
                                                             _body_style='bare')
        def put(ctx, obj):
            return Dal(ctx).put(obj)


    return ReadService, WriteService
