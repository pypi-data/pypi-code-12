from collections import defaultdict
from projex.lazymodule import lazy_import
from projex.locks import ReadWriteLock, ReadLocker, WriteLocker

orb = lazy_import('orb')


class CollectionIterator(object):
    def __init__(self, collection, batch=1):
        self.__collection = collection
        self.__model = collection.model()
        self.__page = 1
        self.__index = -1
        self.__pageSize = batch
        self.__records = []

    def __iter__(self):
        return self

    def next(self):
        self.__index += 1

        # get the next batch of records
        if len(self.__records) in (0, self.__pageSize) and self.__index == len(self.__records):
            sub_collection = self.__collection.page(self.__page, pageSize=self.__pageSize, returning='values')
            self.__records = sub_collection.records()
            self.__page += 1
            self.__index = 0

        # stop the iteration when complete
        if not self.__records or self.__index == len(self.__records):
            raise StopIteration()
        else:
            if self.__collection.context().inflated:
                return self.__model.inflate(self.__records[self.__index], context=self.__collection.context())
            else:
                return self.__records[self.__index]


class Collection(object):
    def __json__(self):
        context = self.context()
        expand = context.expandtree()

        output = {}

        use_records = False

        if expand.pop('count', None) is not None:
            use_records = True
            output['count'] = self.count()

        if expand.pop('ids', None) is not None:
            use_records = True
            output['ids'] = self.ids()

        if expand.pop('first', None) is not None:
            use_records = True
            record = self.first()
            output['first'] = record.__json__() if record else None

        if expand.pop('last', None) is not None:
            use_records = True
            record = self.last()
            output['last'] = record.__json__() if record else None

        if not output or expand:
            records = [record.__json__() if hasattr(record, '__json__') else record for record in self.records()]
            if not use_records:
                return records
            else:
                output['records'] = records

        return output

    def __init__(self, records=None, model=None, source='', record=None, pipe=None, preload=None, **context):
        self.__cacheLock = ReadWriteLock()
        self.__cache = defaultdict(dict)
        self.__preload = preload or {}
        self.__context = orb.Context(**context)
        self.__model = model
        self.__source = source
        self.__record = record
        self.__pipe = pipe

        if records is not None and len(records) > 0:
            if self.__model is None:
                self.__model = type(records[0])

            self.__cache['records'][self.__context] = records

    def __len__(self):
        return self.count()

    def __iter__(self):
        for record in self.records():
            yield record

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.copy(start=index.start, limit=(index.stop - index.start))
        else:
            record = self.at(index)
            if not record:
                raise IndexError(index)
            else:
                return record

    def _process(self, raw, context):
        if context.inflated and context.returning != 'values':
            records = [self.__model.inflate(x, context=context) for x in raw or []]
        elif context.columns:
            schema = self.__model.schema()
            if context.returning == 'values':
                if len(context.columns) == 1:
                    col = schema.column(context.columns[0])
                    records = [x[col.field()] for x in raw or []]
                else:
                    cols = [schema.column(col) for col in context.columns]
                    records = [tuple(r.get(col.field()) for col in cols) for r in raw or []]
            else:
                cols = [schema.column(col) for col in context.columns]
                records = [{col.field(): r.get(col.field()) for col in cols} for r in raw or []]
        else:
            records = raw
        return records

    def add(self, record):
        if self.__pipe:
            cls = self.__pipe.throughModel()
            data = {
                self.__pipe.from_(): self.__record,
                self.__pipe.to(): record
            }
            return cls.ensureExists(data)
        elif self.__source:
            record.set(self.__source, self.__record)
            record.save()
            return True
        else:
            try:
                records = self.__cache['records'][self.__context]
            except KeyError:
                if self.__model is None or type(record) == self.__model:
                    self.__model = type(record)
                    self.__cache['records'][self.__context] = []
                else:
                    raise NotImplementedError

            records.append(record)
            return True

    def at(self, index, **context):
        records = self.records(**context)
        try:
            return records[index]
        except IndexError:
            return None

    def clear(self):
        with WriteLocker(self.__cacheLock):
            self.__cache = defaultdict(dict)

    def create(self, values, **context):
        # create a new pipe object
        if self.__pipe:
            target_model = self.__pipe.toModel()
            target_col = self.__pipe.toColumn()

            # add the target based on the name or field
            if target_col.name() in values or target_col.field() in values:
                record = values.get(target_col.name(), values.get(target_col.field()))
                if not isinstance(record, orb.Model):
                    record = target_model(record)
                self.add(record)
            else:
                record = target_model(values)
                record.save()
                self.add(record)

        # create a new record for this collection
        else:
            if self.__source:
                values.setdefault(self.__source, self.__record)
            record = self.__model.create(values, **context)
            self.add(record)

        return record

    def context(self, **context):
        new_context = self.__context.copy()
        new_context.update(context)
        return new_context

    def copy(self, **context):
        context = self.context(**context)

        with ReadLocker(self.__cacheLock):
            records = self.__cache['records'].get(context)

        other = orb.Collection(
            records=records,
            preload=self.__preload,
            model=self.__model,
            record=self.__record,
            source=self.__source,
            context=context
        )
        return other

    def count(self, **context):
        if self.isNull():
            return 0

        context = self.context(**context)
        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['count'][context]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    return len(self.__cache['records'][context])
            except KeyError:
                optimized_context = context.copy()
                optimized_context.columns = [self.__model.schema().idColumn()]
                optimized_context.expand = None
                optimized_context.order = None

                try:
                    with ReadLocker(self.__cacheLock):
                        count = self.__preload['count'][context]
                except KeyError:
                    try:
                        with ReadLocker(self.__cacheLock):
                            raw = self.__preload['records'][context]
                            count = len(raw)
                    except KeyError:
                        conn = optimized_context.db.connection()
                        count = conn.count(self.__model, optimized_context)

                with WriteLocker(self.__cacheLock):
                    self.__cache['count'][context] = count
                return count

    def delete(self, **context):
        context = orb.Context(**context)
        pipe = self.__pipe

        # delete piped records
        if pipe:
            through = pipe.throughModel()

            # collect the ids that are within this pipe
            base_context = self.context()
            ids = self.ids()

            # remove them from the system
            q = orb.Query(pipe.target()).in_(ids)
            base_context.where = q

            records = through.select(where=q, context=base_context)
            delete = []
            for record in records:
                event = orb.events.DeleteEvent()
                record.onDelete(event)
                if not event.preventDefault:
                    delete.append(record)

            conn = base_context.db.connection()
            return conn.delete(delete, base_context)[1]

        # delete normal records
        else:
            records = self.records(context=context)
            if not records:
                return 0

            # process the deletion event
            remove = []
            for record in records:
                event = orb.events.DeleteEvent()
                record.onDelete(event)
                if not event.preventDefault:
                    remove.append(record)

            # remove the records
            conn = context.db.connection()
            return conn.delete(remove, context)[1]

    def empty(self):
        return self.update([])

    def first(self, **context):
        if self.isNull():
            return None

        context = self.context(**context)

        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['first'][context]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    return self.__cache['first'][context]
            except IndexError:
                return None
            except KeyError:
                try:
                    with ReadLocker(self.__cacheLock):
                        raw = self.__preload['first'][context]
                except KeyError:
                    context.limit = 1
                    context.order = '-id'
                    records = self.records(context=context)
                    record = records[0] if records else None
                else:
                    record = self._process([raw], context)[0]

                with WriteLocker(self.__cacheLock):
                    self.__cache['first'][context] = record
                return record

    def grouped(self, *columns, **context):
        preload = context.pop('preload', False)

        output = {}

        if preload:
            records = self.records(**context)
            for record in records:
                data = output
                for column in columns[:-1]:
                    key = record[column]
                    data.setdefault(key, {})
                    data = data[key]

                key = record[columns[-1]]
                data.setdefault(key, orb.Collection())
                data[key].add(record)
        else:
            values = self.values(*columns, **context)

            for value in values:
                data = output
                q = orb.Query()
                for i, column in enumerate(columns[:-1]):
                    key = value[i]
                    data.setdefault(key, {})
                    data = data[key]

                    q &= orb.Query(column) == key

                key = value[-1]
                q &= orb.Query(columns[-1]) == key

                group_context = context.copy()
                group_context['where'] = q & group_context.get('where')
                data.setdefault(key, self.refine(**group_context))

            return output

    def has(self, record, **context):
        context = self.context(**context)
        context.returning = 'values'
        context.columns = ['id']
        return self.first(context=context) is not None

    def ids(self, **context):
        if self.isNull():
            return []

        context = self.context(**context)
        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['ids'][context]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    ids = self.__preload['ids'][context]
            except KeyError:
                ids = self.records(columns=['id'], returning='values', context=context)

            with WriteLocker(self.__cacheLock):
                self.__cache['ids'][context] = ids

            return ids

    def index(self, record, **context):
        context = self.context(**context)
        if not record:
            return -1
        else:
            try:
                with ReadLocker(self.__cacheLock):
                    return self.__cache['records'][context].index(record)
            except KeyError:
                return self.ids().index(record.id())

    def isLoaded(self, **context):
        context = self.context(**context)
        with ReadLocker(self.__cacheLock):
            return context in self.__cache['records']

    def isEmpty(self, **context):
        return self.count(**context) == 0

    def isNull(self):
        with ReadLocker(self.__cacheLock):
            return self.__cache['records'].get(self.__context) is None and self.__model is None

    def iterate(self, batch=100):
        return CollectionIterator(self, batch)

    def last(self, **context):
        if self.isNull():
            return None

        context = self.context(**context)
        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['last'][context]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    raw = self.__preload['last'][context]
            except KeyError:
                record = self.reversed().first(context=context)
            else:
                record = self._process([raw], context)[0]

            with WriteLocker(self.__cacheLock):
                self.__cache['last'][context] = record
            return record

    def model(self):
        return self.__model

    def ordered(self, order):
        """
        Return a copy of this collection with the new order sequence.

        :param order:  <str> || (<str>, <str> 'ASC' || 'DESC')

        :return: <orb.Collection>
        """
        return self.copy(order=order)

    def page(self, number, **context):
        """
        Returns the records for the current page, or the specified page number.
        If a page size is not specified, then this record sets page size will
        be used.

        :param      pageno   | <int>
                    pageSize | <int>

        :return     <orb.RecordSet>
        """
        size = max(0, self.context(**context).pageSize)
        if not size:
            return self.copy()
        else:
            return self.copy(page=number, pageSize=size)

    def pageCount(self, **context):
        size = max(0, self.context(**context).pageSize)

        if not size:
            return 1
        else:
            context['page'] = None
            context['limit'] = None
            
            fraction = self.count(**context) / float(size)
            count = int(fraction)
            if count % 1:
                count += 1
            return max(1, count)

    def pipe(self):
        return self.__pipe

    def preload(self, cache, **context):
        context = self.context(**context)
        with WriteLocker(self.__cacheLock):
            for key, value in cache.items():
                self.__preload.setdefault(key, {})
                self.__preload[key][context] = value

    def records(self, **context):
        if self.isNull():
            return []

        context = self.context(**context)

        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['records'][context]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    raw = self.__preload['records'][context]
            except KeyError:
                conn = context.db.connection()
                raw = conn.select(self.__model, context)

            records = self._process(raw, context)

            with WriteLocker(self.__cacheLock):
                self.__cache['records'][context] = records
            return records

    def refine(self, createNew=True, **context):
        if not createNew:
            self.__context.update(context)
            return self
        else:
            context = self.context(**context)
            with ReadLocker(self.__cacheLock):
                records = self.__cache['records'].get(context)

            other = orb.Collection(
                records=records,
                model=self.__model,
                record=self.__record,
                source=self.__source,
                context=context
            )
            return other

    def remove(self, record, **context):
        pipe = self.__pipe
        if pipe:
            through = pipe.throughModel()
            q  = orb.Query(pipe.from_()) == self.__record
            q &= orb.Query(pipe.to()) == record

            context['where'] = q & context.get('where')
            context = self.context(**context)

            records = through.select(context=context)
            delete = []
            for record in records:
                event = orb.events.DeleteEvent()
                record.onDelete(event)
                if not event.preventDefault:
                    delete.append(record)

            conn = context.db.connection()
            conn.delete(records, context)

            return len(delete)
        elif self.__source:
            record.set(self.__source, None)
            record.save()
            return 1
        else:
            raise NotImplementedError

    def reversed(self):
        collection = self.copy()
        context = collection.context()
        order = [(col, 'asc' if dir == 'desc' else 'desc') for col, dir in context.order or []] or None
        collection.refine(order=order)
        return collection

    def search(self, terms, **context):
        """
        Searches for records within this collection based on the given terms.

        :param terms: <str>
        :param context: <orb.Context>

        :return: <orb.SearchResultCollection>
        """
        return self.model().searchEngine().search(terms, self.context(**context))

    def update(self, records, **context):
        # clean up the records for removal
        if isinstance(records, dict):
            if 'ids' in records:
                ids = records.get('ids')
            elif 'records' in records:
                ids = [r.get('id') for r in records['records'] if r.get('id')]
            else:
                raise orb.errors.OrbError('Invalid input for collection update: {0}'.format(records))

        elif isinstance(records, (list, set, tuple)):
            ids = []
            for record in records:
                if isinstance(record, orb.Model):
                    ids.append(record.id())
                else:
                    ids.append(record)

        elif isinstance(records, orb.Collection):
            ids = records.ids()

        else:
            raise orb.errors.OrbError('Invalid input for collection update: {0}'.format(records))

        # update a pipe
        if self.__pipe:
            through = self.__pipe.throughModel()
            pipe = self.__pipe
            curr_ids = self.ids()

            remove_ids = set(curr_ids) - set(ids)
            add_ids = set(ids) - set(curr_ids)

            # remove old records
            if remove_ids:
                q  = orb.Query(through, pipe.from_()) == self.__record
                q &= orb.Query(through, pipe.to()).in_(remove_ids)
                through.select(where=q).delete()

            # create new records
            if add_ids:
                collection = orb.Collection([through({pipe.from_(): self.__record, pipe.to(): id})
                                             for id in add_ids])
                collection.save()

            return len(add_ids), len(remove_ids)

        # udpate a reverse lookup
        elif self.__source:
            model = self.__source.schema().model()

            q = orb.Query(self.__source) == self.__record
            if ids:
                q &= orb.Query(model).notIn(ids)

            # determine the reverse lookups to remove from this collection
            remove = model.select(where=q, **context)
            for record in remove:
                record.set(self.__source, None)
                record.save()

            # determine the new records to add to this collection
            if ids:
                q  = orb.Query(model).in_(ids)
                q &= (orb.Query(self.__source) != self.__record) | (orb.Query(self.__source) == None)

                add = model.select(where=q)
                for record in add:
                    record.set(self.__source, self.__record)
                    record.save()

        else:
            raise NotImplementedError

    def save(self, **context):
        records = self.records(**context)
        context = self.context(**context)
        conn = context.db.connection()

        create_records = []
        update_records = []

        # run the pre-commit event for each record
        for record in records:
            event = orb.events.SaveEvent(context=context, newRecord=not record.isRecord())
            record.onPreSave(event)
            if not event.preventDefault:
                if record.isRecord():
                    update_records.append(record)
                else:
                    create_records.append(record)

        # save and update the records
        if create_records:
            results, _ = conn.insert(create_records, context)

            # store the newly generated ids
            for i, record in enumerate(create_records):
                record.update(results[i])

        if update_records:
            conn.update(update_records, context)

        # run the post-commit event for each record
        for record in create_records + update_records:
            event = orb.events.SaveEvent(context=context, newRecord=record in create_records)
            record.onPostSave(event)

        return True

    def setModel(self, model):
        self.__model = model

    def setPipe(self, pipe):
        self.__pipe = pipe

    def values(self, *columns, **context):
        if self.isNull():
            return None

        context = self.context(**context)

        try:
            with ReadLocker(self.__cacheLock):
                return self.__cache['values'][(context, columns)]
        except KeyError:
            try:
                with ReadLocker(self.__cacheLock):
                    raw = self.__preload['records'][context]
            except KeyError:
                context.columns = columns
                conn = context.db.connection()
                raw = conn.select(self.__model, context)

            schema = self.__model.schema()
            values = []
            fields = [schema.column(col) for col in columns]
            for record in raw:
                record_values = [record[field] for field in record]
                if len(fields) == 1:
                    values.append(record_values[0])
                else:
                    values.append(record_values)

            with WriteLocker(self.__cacheLock):
                self.__cache['values'][(context, columns)] = values

            return values
