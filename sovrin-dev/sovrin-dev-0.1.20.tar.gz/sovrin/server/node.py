import asyncio
import json
import os
import platform

import time
from _sha256 import sha256

import pyorient

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.request_types import Reply, Request, RequestAck, RequestNack
from plenum.server.node import Node as PlenumNode
from sovrin.common.has_file_storage import HasFileStorage

from sovrin.common.txn import getGenesisTxns, TXN_TYPE, \
    TARGET_NYM, allOpKeys, validTxnTypes, ADD_ATTR, SPONSOR, ADD_NYM, ROLE, \
    STEWARD, USER, GET_ATTR, DISCLOSE, ORIGIN, DATA, NONCE, GET_NYM, TXN_ID, \
    TXN_TIME, ATTRIBUTES, REFERENCE, reqOpKeys, GET_TXNS, LAST_TXN, TXNS
from sovrin.persistence.graph_store import GraphStore
from sovrin.persistence.ledger_chain_store import LedgerChainStore
from sovrin.server.client_authn import TxnBasedAuthNr
from sovrin.common.util import getConfig


async def eventually(condition, *args, timeout=5):
    result = False
    start = time.perf_counter()
    elapsed = 0
    while elapsed < timeout:
        result = condition(*args)
        if result:
            break
        await asyncio.sleep(.1)
        elapsed = time.perf_counter() - start
    return result


# TODO Node storage should be a mixin of document storage and graph storage

class Node(PlenumNode, HasFileStorage):

    def __init__(self,
                 name,
                 nodeRegistry,
                 clientAuthNr=None,
                 ha=None,
                 cliname=None,
                 cliha=None,
                 basedirpath=None,
                 primaryDecider=None,
                 opVerifiers=None,
                 storage=None,
                 config=None):

        self.config = config or getConfig()
        self.graphStorage = self.getGraphStorage(name)

        self.dataDir = "data/nodes"
        if not storage:
            HasFileStorage.__init__(self, name, baseDir=basedirpath,
                                    dataDir=self.dataDir)
            storage = LedgerChainStore(name, self.getDataLocation())

        super().__init__(name=name,
                         nodeRegistry=nodeRegistry,
                         clientAuthNr=clientAuthNr,
                         ha=ha,
                         cliname=cliname,
                         cliha=cliha,
                         basedirpath=basedirpath,
                         primaryDecider=primaryDecider,
                         opVerifiers=opVerifiers,
                         storage=storage,
                         config=self.config)

    # async def prod(self, limit: int=None):
    #     await self.setup()
    #     return await super().prod(limit)
    #
    # async def setup(self):
    #     if not self.setupComplete:
    #         self.graphStorage = await self.getGraphStorage(self.name)
    #         self.setupComplete = True
    #
    # async def getGraphStorage(self, name):
    #     config = getConfig()
    #     result = await self.ensureDBAvailable(config)
    #     if result:
    #         return self.createGraphStorage(name, config)
    #
    # @staticmethod
    # async def ensureDBAvailable(config):
    #     """
    #     Starts the graph database if not already started.
    #     """
    #     if platform.system() == 'Linux':
    #         # TODO If exit code is 256, throw an exception and abort.
    #         # TODO Don't use os.system at all. The return codes are unreliable.
    #         # TODO Try connecting to the orientdb instance to check if it's up.
    #         if os.system("service orientdb status"):
    #             return True
    #         else:
    #             # TODO
    #             os.system("{} &".format(config.GraphDB["startScript"]))
    #             return await eventually(os.system, "service orientdb status")
    #     elif platform.system() == 'Windows':
    #         pass  # TODO when a Windows machine is available

    # @staticmethod
    # def createGraphStorage(name, config):
    #     return GraphStore(user=config.GraphDB["user"],
    #                         password=config.GraphDB["password"],
    #                         dbName=name,
    #                         storageType=pyorient.STORAGE_TYPE_PLOCAL)

    def getGraphStorage(self, name):
        return GraphStore(user=self.config.GraphDB["user"],
                          password=self.config.GraphDB["password"],
                          dbName=name,
                          storageType=pyorient.STORAGE_TYPE_PLOCAL)

    # TODO: Should adding of genesis transactions be part of start method
    def addGenesisTxns(self, genTxns=None):
        if self.txnStore.size == 0:
            gt = genTxns or getGenesisTxns()
            for idx, txn in enumerate(gt):
                reply = Reply(0, idx, txn)
                asyncio.ensure_future(
                    self.txnStore.append("", reply, txn[TXN_ID]))
                if txn[TXN_TYPE] == ADD_NYM:
                    self.addNymToGraph(txn)
                # Till now we just have ADD_NYM in genesis transaction.

    def addNymToGraph(self, txn):
        if ROLE not in txn or txn[ROLE] == USER:
            self.graphStorage.addUser(txn[TXN_ID], txn[TARGET_NYM], txn[ORIGIN],
                                      reference=txn.get(REFERENCE))
        elif txn[ROLE] == SPONSOR:
            self.graphStorage.addSponsor(txn[TXN_ID], txn[TARGET_NYM], txn[ORIGIN])
        elif txn[ROLE] == STEWARD:
            self.graphStorage.addSteward(txn[TXN_ID], txn[TARGET_NYM], txn.get(ORIGIN))
        else:
            raise ValueError("Unknown role for nym, cannot add nym to graph")

    def checkValidOperation(self, identifier, reqId, msg):
        self.checkValidSovrinOperation(identifier, reqId, msg)
        super().checkValidOperation(identifier, reqId, msg)

    def checkValidSovrinOperation(self, identifier, reqId, msg):
        unknownKeys = set(msg.keys()).difference(set(allOpKeys))
        if unknownKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'invalid keys "{}"'.
                                       format(",".join(unknownKeys)))

        missingKeys = set(reqOpKeys).difference(set(msg.keys()))
        if missingKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'missing required keys "{}"'.
                                       format(",".join(missingKeys)))

        if msg[TXN_TYPE] not in validTxnTypes:
            raise InvalidClientRequest(identifier, reqId, 'invalid {}: {}'.
                                       format(TXN_TYPE, msg[TXN_TYPE]))

        if msg[TXN_TYPE] == ADD_ATTR:
            if TARGET_NYM not in msg:
                raise InvalidClientRequest(identifier, reqId,
                                           '{} operation requires {} attribute'.
                                           format(ADD_ATTR, TARGET_NYM))
            if not self.graphStorage.hasNym(msg[TARGET_NYM]):
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should be added before adding '
                                           'attribute for it'.
                                           format(TARGET_NYM))

        if msg[TXN_TYPE] == ADD_NYM:
            if self.graphStorage.hasNym(msg[TARGET_NYM]):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} is already present".
                                           format(msg[TARGET_NYM]))

    authorizedAdders = {
        USER: (STEWARD, SPONSOR),
        SPONSOR: (STEWARD,)
    }

    async def checkRequestAuthorized(self, request: Request):
        op = request.operation
        typ = op[TXN_TYPE]

        s = self.graphStorage  # type: GraphStore

        origin = request.identifier
        originRole = s.getRole(origin)

        if typ == ADD_NYM:
            role = op.get(ROLE, USER)
            authorizedAdder = self.authorizedAdders[role]
            if originRole not in authorizedAdder:
                raise UnauthorizedClientRequest(
                    request.identifier,
                    request.reqId,
                    "{} cannot add {}".format(originRole, role))
        elif typ == ADD_ATTR:
            if not s.getSponsorFor(op[TARGET_NYM]) == origin:
                raise UnauthorizedClientRequest(
                        request.identifier,
                        request.reqId,
                        "Only user's sponsor can add attribute for that user")
        # TODO: Just for now. Later do something meaningful here
        elif typ in [DISCLOSE, GET_ATTR]:
            pass
        else:
            raise UnauthorizedClientRequest(
                    request.identifier,
                    request.reqId,
                    "Assuming no one is authorized for txn type {}".format(typ))

    def defaultAuthNr(self):
        return TxnBasedAuthNr(self.graphStorage)

    @staticmethod
    def genTxnId(identifier, reqId):
        return sha256("{}{}".format(identifier, reqId).encode()).hexdigest()

    async def processRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == GET_NYM:
            self.transmitToClient(RequestAck(request.reqId), frm)
            nym = request.operation[TARGET_NYM]
            txn = self.graphStorage.getAddNymTxn(nym)
            txnId = self.genTxnId(request.identifier, request.reqId)
            result = {DATA: json.dumps(txn) if txn else None,
                      TXN_ID: txnId,
                      TXN_TIME: time.time()*1000
                      }
            result.update(request.operation)
            self.transmitToClient(Reply(self.viewNo, request.reqId, result), frm)
        elif request.operation[TXN_TYPE] == GET_TXNS:
            nym = request.operation[TARGET_NYM]
            origin = request.operation[ORIGIN]
            if nym != origin:
                msg = "You can only receive transactions for yourself"
                self.transmitToClient(RequestNack(request.reqId, msg), frm)
            else:
                data = request.operation.get(DATA)
                self.transmitToClient(RequestAck(request.reqId), frm)
                addNymTxn = self.graphStorage.getAddNymTxn(origin)
                txnIds = [addNymTxn[TXN_ID], ] + self.graphStorage.getAddAttributeTxnIds(origin)
                result = self.txnStore.getRepliesForTxnIds(*txnIds, serialNo=data)
                lastTxn = max(result.keys()) if len(result) > 0 else 0
                txns = list(result.values())
                result = {
                    DATA: json.dumps({
                        LAST_TXN: lastTxn,
                        TXNS: txns
                    }),
                    TXN_ID: self.genTxnId(request.identifier, request.reqId),
                    TXN_TIME: time.time() * 1000
                }
                result.update(request.operation)
                self.transmitToClient(Reply(self.viewNo, request.reqId, result),
                                      frm)
        else:
            await super().processRequest(request, frm)

    async def addToLedger(self, identifier, reply, txnId):
        merkleInfo = await self.txnStore.append(
            identifier=identifier, reply=reply, txnId=txnId)
        serialNo = merkleInfo["serialNo"]
        STH = merkleInfo["STH"]
        auditInfo = merkleInfo["auditInfo"]
        # TODO Do both operation in one request
        self.txnStore.addReplyForTxn(txnId, reply, identifier, reply.reqId)
        self.txnStore.addMerkleDataForTxn(txnId, serialNo, STH, auditInfo)
        return merkleInfo

    async def storeTxnAndSendToClient(self, identifier, reply, txnId):
        merkleInfo = await self.addToLedger(identifier, reply, txnId)
        reply.result.update(merkleInfo)
        self.transmitToClient(reply, self.clientIdentifiers[identifier])

    def storeProcessedRequest(self, identifier, reply, txnId):
        asyncio.ensure_future(self.addToLedger(identifier, reply, txnId))

    async def getReplyFor(self, identifier, reqId):
        return self.txnStore.getReply(identifier, reqId)

    def doCustomAction(self, viewNo: int, ppTime: float, req: Request) -> None:
        """
        Execute the REQUEST sent to this Node

        :param viewNo: the view number (See glossary)
        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST
        """
        reply = self.generateReply(viewNo, ppTime, req)
        txnId = reply.result[TXN_ID]
        asyncio.ensure_future(self.storeTxnAndSendToClient(req.identifier,
                                                           reply, txnId))

    def generateReply(self, viewNo: int, ppTime: float, req: Request):
        operation = req.operation
        txnId = self.genTxnId(req.identifier, req.reqId)
        result = {TXN_ID: txnId, TXN_TIME: ppTime}
        # if operation[TXN_TYPE] == GET_ATTR:
        #     # TODO: Very inefficient, queries all transactions and looks for the
        #     # DISCLOSE for the clients and returns all. We probably change the
        #     # transaction schema or have some way to zero in on the DISCLOSE for
        #     # the attribute that is being looked for
        #     attrs = []
        #     for txn in self.txnStore.getAllTxn().values():
        #         if txn.get(TARGET_NYM, None) == req.identifier and txn[TXN_TYPE] == \
        #                 DISCLOSE:
        #             attrs.append({DATA: txn[DATA], NONCE: txn[NONCE]})
        #     if attrs:
        #         result[ATTRIBUTES] = attrs
        # TODO: Just for the time being. Remove ASAP
        result.update(operation)
        if operation[TXN_TYPE] == ADD_NYM:
            self.addNymToGraph(result)
        elif operation[TXN_TYPE] == ADD_ATTR:
            self.graphStorage.addAttribute(frm=operation[ORIGIN],
                                           to=operation[TARGET_NYM],
                                           data=operation[DATA],
                                           txnId=txnId)
        return Reply(viewNo,
                     req.reqId,
                     result)

