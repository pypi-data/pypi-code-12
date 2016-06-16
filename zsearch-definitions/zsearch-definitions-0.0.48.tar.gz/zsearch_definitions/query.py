import sys
import os.path
import base64
import argparse
import datetime
import time
import json
import hashlib
import struct
import socket

from zsearch_definitions import search_pb2
from zsearch_definitions import protocols_pb2
from zsearch_definitions import rpc_pb2
from zsearch_definitions import common_pb2
from zsearch_definitions import anonstore_pb2
from zsearch_definitions import hoststore_pb2

import zsearch_definitions.protocols

class QueryService(object):

    TIMEOUT = 30 # second
    HOST = "localhost"
    PORT = 9090

    HQ_SUCCESS = rpc_pb2.HostQueryResponse.ResponseStatus.Value("SUCCESS")
    HQ_RESERVED= rpc_pb2.HostQueryResponse.ResponseStatus.Value("RESERVED")
    HQ_NO_RECORD = rpc_pb2.HostQueryResponse.ResponseStatus.Value("NO_RECORD")
    HQ_ERROR = rpc_pb2.HostQueryResponse.ResponseStatus.Value("ERROR")

    AQ_SUCCESS = rpc_pb2.AnonymousQueryResponse.ResponseStatus.Value("SUCCESS")
    AQ_RESERVED= rpc_pb2.AnonymousQueryResponse.ResponseStatus.Value("RESERVED")
    AQ_NO_RECORD = rpc_pb2.AnonymousQueryResponse.ResponseStatus.Value("NO_RECORD")
    AQ_ERROR = rpc_pb2.AnonymousQueryResponse.ResponseStatus.Value("ERROR")

    @staticmethod
    def _port_to_pb(port):
        return socket.htons(port)

    @staticmethod
    def _ip_to_pb(ip):
        if isinstance(ip, (str, unicode)):
            network_bytes = socket.inet_aton(ip)
            (network_int, ) = struct.unpack("I", network_bytes)
            return network_int
        return socket.htonl(ip)

    @staticmethod
    def _get_atom_fp(atom):
        a = atom.SerializeToString()
        m = hashlib.sha256()
        m.update(a)
        return m.digest()

    def __init__(self, host=None, port=None):
        port = port or self.PORT
        host = host or self.HOST
        self._service = search_pb2.early_adopter_create_QueryService_stub(host,
                port).__enter__()

    @property
    def service(self):
        return self._service

    def get_certificate(self, sha256_fp):
        aq = rpc_pb2.AnonymousQuery(
                sha256fp=b64decode(sha256_fp))
        res = self._service.GetCertificate(aq)
        assert(resp.status != self.AQ_RESERVED)
        if resp.status == self.AQ_ERROR:
            raise Exception("Request failed: %s" % resp.error)
        elif resp.status == self.AQ_NO_RECORD:
            return None
        else: # (SUCCESS)
            return resp.certificate


    def put_certificate(self, raw, parsed):
        sha256_fp = parsed["fingerprint_sha256"].decode("hex")
        sha1_fp = parsed["fingerprint_sha1"].decode("hex")
        c = anonstore_pb2.Certificate(
                sha1fp=sha1_fp,
                sha256fp=sha256_fp,
                raw=base64.b64decode(raw),
                parsed=json.dumps(parsed, sort_keys=True)
        )
        ar = anonstore_pb2.AnonymousRecord(
                sha256fp=sha256_fp,
                timestamp=self._get_int_timestamp(),
                exported=False,
                certificate=c
        )
        return self._service.UpsertCertificate(ar, self.TIMEOUT)
    
    def put_raw_certificate(self, rawcert):
        return self._service.UpsertRawCertificate(rawcert, self.TIMEOUT)


    def _get_host_record(self, meth, ip, domain, port, proto, subproto):
        ip = self._ip_to_pb(ip) if ip else 0
        port = self._port_to_pb(port)
	proto = zsearch_definitions.protocols.Protocol.from_pretty_name(proto)
	subproto = zsearch_definitions.protocols.Subprotocol.from_pretty_name(subproto)
        host_query = rpc_pb2.HostQuery(
                        ip=ip,
                        domain=domain,
                        port=port,
                        protocol=proto.value,
                        subprotocol=subproto.value
                     )
        resp = meth(host_query, self.TIMEOUT)
        assert(resp.status != self.HQ_RESERVED)
        if resp.status == self.HQ_ERROR:
            raise Exception("Request failed: %s" % resp.error)
        elif resp.status == self.HQ_NO_RECORD:
            return None
        else: # (SUCCESS)
            return resp.record

    def get_host_ipv4_record(self, ip, port, proto, subproto):
        return self._get_host_record(self._service.GetHostIPv4Record,
            ip, "", port, proto, subproto)

    def get_host_domain_record(self, domain, port, proto, subproto):
        return self._get_host_record(self._service.GetHostDomainRecord,
            None, domain, port, proto, subproto)

    @staticmethod
    def _get_int_timestamp():
        return int(time.mktime(datetime.datetime.now().timetuple()))

    def _make_atom(self, data, tags, metadata):
        metadatums = []
        for k, v in (metadata or {}).items():
            m = common_pb2.Metadatum(key=k, value=v)
            metadatums.append(m)
        atom = hoststore_pb2.ProtocolAtom(metadata=metadatums,
                tags=(tags or []), data=data)
        return atom

    def put_host_ipv4_record(self, ip, port, proto, subproto,
            data, tags=None, metadata=None):
        atom = self._make_atom(data, tags, metadata)
        fp = self._get_atom_fp(atom)
        record = hoststore_pb2.Record(
                    ip=self._ip_to_pb(ip),
                    port=self._port_to_pb(port),
                    protocol=protocols_pb2.Protocol.Value(proto),
                    subprotocol=protocols_pb2.Subprotocol.Value(subproto),
                    timestamp=self._get_int_timestamp(),
                    atom=atom,
                    sha256fp=fp,
                 )
        return self._service.PutHostIPv4Record(record, self.TIMEOUT)

    def put_host_domain_record(self, domain, ip, port, proto, subproto,
            data, tags=None, metadata=None):
        atom = self._make_atom(data, tags, metadata)
        fp = self._get_atom_fp(atom)
        record = hoststore_pb2.Record(
                    domain=domain,
                    ip=self._ip_to_pb(ip),
                    port=self._port_to_pb(port),
                    protocol=protocols_pb2.Protocol.Value(proto),
                    subprotocol=protocols_pb2.Subprotocol.Value(subproto),
                    timestamp=self._get_int_timestamp(),
                    atom=atom
                 )
        return self._service.PutHostDomainRecord(record, self.TIMEOUT)

    def delete_host_ipv4_record(self, ip, port, proto, subproto):
        ip = self._ip_to_pb(ip)
        port = self._port_to_pb(port)
        proto = protocols_pb2.Protocol.Value(proto)
        subproto = protocols_pb2.Subprotocol.Value(subproto)
        host_query = rpc_pb2.HostQuery(
                        ip=ip,
                        port=port,
                        proto=proto,
                        subproto=subproto
                     )
        return self._service.DelHostIPv4Record(host_query, self.TIMEOUT)

    def delete_host_domain_record(self, domain, port, proto, subproto):
        port = self._port_to_pb(port)
        proto = zsearch_definitions.protocols.Protocol.from_pretty_name(proto)
        subproto = zsearch_definitions.protocols.Subprotocol.from_pretty_name(subproto)
        host_query = rpc_pb2.HostQuery(
                        domain=domain,
                        port=port,
                        protocol=proto.value,
                        subprotocol=subproto.value
                     )
        return self._service.DelHostDomainRecord(host_query, self.TIMEOUT)

    def get_host_ipv4_userdata(self, ip):
        raise Exception("not implemented.")

    def put_host_ipv4_userdata(self, ip, userdata):
        raise Exception("not implemented.")

    def iter_host_records(self, meth, max_records):
        resp = meth(rpc_pb2.HostQuery(max_records=max_records), self.TIMEOUT)
        assert(resp.status != self.HQ_RESERVED)
        if resp.status == self.HQ_ERROR:
            raise Exception("Request failed: %s" % resp.error)
        for r in resp.records:
            yield r

    def iter_ipv4_records(self, max_records=0):
        for record in self.iter_host_records(self._service.GetAllIPv4Records, max_records):
            yield record

    def iter_domain_records(self, max_records=0):
        for record in self.iter_host_records(self._service.GetAllDomainRecords, max_records):
            yield record

    def __del__(self):
        if self._service:
            self._service.__exit__(None, None, None)

if __name__ == "__main__":
   q = QueryService()
   print q.get_host_ipv4_record(1046726718, 443, "https", "tls")
