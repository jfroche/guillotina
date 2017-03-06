import asyncio
import asyncpg
import logging


class DummyStorage(object):
    """Storage to a relational database, based on invalidation polling"""

    _last_transaction = 0
    _last_oid = 0

    # MAIN MEMORY DB OBJECT OID -> OBJ
    DB = {}

    # PARENT_ID_ID INDEX
    # TUPLE (PARENT_OID + ID) -> OID
    PARENT_ID_ID = {}

    # PARENT_ID INDEX (OID -> LIST OID)
    PARENT_ID = {}

    def __init__(self, folder=None):
        self._folder = folder
        self._lock = asyncio.Lock()
        self.read_conn = None

    def isReadOnly(self):
        return self._read_only

    async def finalize(self):
        pass

    async def initialize(self, loop=None):
        pass

    async def remove(self):
        """Reset the tables"""
        pass

    async def open(self):
        return None

    async def close(self, con):
        pass

    async def last_transaction(self, txn):
        return self._last_transaction

    async def next_tid(self, txn):
        async with self._lock:
            self._last_transaction += 1
            return self._last_transaction

    async def next_oid(self, txn):
        async with self._lock:
            self._last_oid += 1
            return self._last_oid

    async def load(self, txn, oid):
        objects = self.DB[oid]
        if objects is None:
            raise KeyError(oid)
        return objects

    async def tpc_begin(self, txn, conn):
        # Add the new tid
        txn._db_txn = {}
        txn._db_conn = conn

    async def precommit(self, txn):
        tid = await self.next_tid(txn)
        if tid is not None:
            txn._tid = tid

    async def store(self, oid, old_serial, writer, obj, txn):
        assert oid is not None
        p = writer.serialize()  # This calls __getstate__ of obj
        json = writer.json
        part = writer.part
        if part is None:
            part = 0
        # (zoid, tid, state_size, part, main, parent_id, type, json, state)
        tobj = {
            'zoid': oid,
            'tid': txn._tid,
            'size': len(p),
            'part': part,
            'resource': writer.resource,
            'of': writer.of,
            'serial': old_serial,
            'parent_id': writer.parent_id,
            'id': writer.id,
            'type': writer.type,
            'json': json,
            'state': p
        }
        txn._db_txn[oid] = tobj
        obj._p_estimated_size = len(p)
        return txn._tid, len(p)

    async def delete(self, txn, oid):
        tobj = self.DB[oid]
        del self.PARENT_ID_ID[(tobj['parent_id'], tobj['id'])]
        self.PARENT_ID[tobj['parent_id']].remove(oid)
        del self.DB[oid]

    async def tpc_vote(self, transaction):
        # Check if there is any commit bigger than the one we already have
        # For each object going to be written we need to check if it has
        # a new TID
        for oid, tobj in transaction._db_txn.items():
            if oid in self.DB:
                if self.DB[oid]['tid'] > tobj['tid']:
                    return False

        return True

    async def tpc_finish(self, transaction):
        for oid, element in transaction._db_txn.items():
            self.DB[oid] = element
            if element['parent_id'] in self.PARENT_ID:
                self.PARENT_ID[element['parent_id']].append(oid)
            else:
                self.PARENT_ID[element['parent_id']] = [oid]
            self.PARENT_ID_ID[(element['parent_id'], element['id'])] = oid

        return transaction._tid

    async def abort(self, transaction):
        transaction._db_txn = None

    # Introspection

    async def keys(self, txn, oid):
        keys = []
        for record in self.PARENT_ID[oid]:
            obj = await self.load(txn, record)
            keys.append(obj['id'])
        return keys

    async def get_child(self, txn, parent_id, id):
        oid = self.PARENT_ID_ID[(parent_id, id)]
        return await self.load(txn, oid)

    async def has_key(self, txn, parent_id, id):
        return True if (parent_id, id) in self.PARENT_ID_ID.keys() else False

    async def len(self, txn, oid):
        return len(self.PARENT_ID[oid])

    async def items(self, txn, oid):
        for record in self.PARENT_ID[oid]:
            obj = await self.load(txn, record)
            yield obj
