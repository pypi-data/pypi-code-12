from . import yaml
from .bases import ModelRef
from .loaders import load
from collections import OrderedDict, namedtuple
from collections.abc import Mapping

Fragment = namedtuple('Fragment', 'ctx, content, path')


class Application(Mapping):

    def __init__(self, content):
        self.content = content

    def __getitem__(self, key):
        return self.content[key]

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)

    def to_yaml(self, **kwargs):
        return yaml.dump(self.content, **kwargs)


class Registry:

    def __init__(self):
        self.documents = OrderedDict()

    def uri_id(self, uri):
        return list(self.documents).index('uri')


class Context:

    def __init__(self, document, registry=None):
        self.document = document
        self.registry = registry or Registry()
        self.registry.documents[document.uri] = document

    @property
    def uri(self):
        return self.document.uri

    @property
    def content(self):
        return self.document.content

    def extract(self, ref):
        uri, _, path = ref.partition('#')
        document = self.get_document(uri) if uri else self.document
        frag = document.content
        path = path or '/'
        if path is not '/':
            for part in path[1:].split('/'):
                try:
                    frag = frag[part]
                except KeyError as error:
                    if part.isdigit():
                        frag = frag[int(part)]
                        break
                    raise error
        return Fragment(Context(document, self.registry), frag, path)

    def get_document(self, document):
        loader = load(document, self.uri)
        if loader.uri in self.registry.documents:
            return self.registry.documents[loader.uri]
        self.registry.documents[loader.uri] = loader.load()
        return self.registry.documents[loader.uri]

    def __getitem__(self, key):
        return self.content[key]

    def __setitem__(self, key):
        return self.content[key]

    def __iter__(self):
        return iter(self.content)

    def __repr__(self):
        return '<Context(uri=%r)>' % self.uri


def resolve(src, granularity=False):
    document = load(src).load()
    assert document.content['swagger'] == '2.0'
    ctx = Context(document)
    # explore and bring back objects into main document
    resolver = Resolver(document.content)
    for path, data in ctx['paths'].items():
        ctx['paths'][path] = resolver.grab(data, ctx)

    if granularity == 'sparse':
        # remerge model schemas
        for model, data in ctx['definitions'].items():
            ctx['definitions'][model] = resolver.merge(data, ctx)
    elif granularity == 'full':
        # remerge everything
        resolver.merge(ctx.content, ctx)
    return Application(ctx.content)


class Resolver:

    def __init__(self, content):
        self.definitions = content['definitions']
        self.parameters = content['parameters']
        self.responses = content['responses']
        self.uris = []

    def grab(self, data, ctx):
        if isinstance(data, dict):
            if '$ref' in data and not isinstance(data['$ref'], ModelRef):
                ref = data.pop('$ref')
                frag = ctx.extract(ref)
                self.grab(frag.content, frag.ctx)

                _, a, model = frag.path.split('/', 2)
                if a in ('definitions', 'responses', 'parameters'):
                    data['$ref'] = self.deifycate(frag)
                else:
                    for key, value in frag.content.items():
                        data.setdefault(key, value)
            for key, value in data.items():
                data[key] = self.grab(value, ctx)
        if isinstance(data, list):
            data = [self.grab(cnt, ctx) for cnt in data]
        return data

    def merge(self, data, ctx):
        if isinstance(data, dict):
            if '$ref' in data:
                ref = data.pop('$ref')
                frag = ctx.extract(ref)
                data = merge_schemas(data, frag.content)
            for key, value in data.items():
                data[key] = self.merge(value, ctx)
            if 'allOf' in data:
                definitions = data.pop('allOf', [])
                data = merge_schemas(data, *definitions)

        if isinstance(data, list):
            data = [self.merge(cnt, ctx) for cnt in data]
        return data

    def deifycate(self, frag):
        path = frag.path
        _, a, b = frag.path.split('/', 2)
        if a in ('definitions', 'responses', 'parameters'):
            repo = getattr(self, a)
            pref = self.prefix(frag.ctx.uri)
            model = '%s%s' % (pref, b)
            if model.isdigit():
                model = int(model)
            if model not in repo:
                repo[model] = frag.content
            return ModelRef('#/%s/%s' % (a, model))
        return '#%s' % path

    def prefix(self, uri):
        if uri not in self.uris:
            self.uris.append(uri)
        index = self.uris.index(uri)
        if index <= 0:
            return ''
        return '%s:' % index


def merge_schemas(target, *definitions):
    for definition in reversed(definitions):
        for attr, attrvalue in definition.items():
            if attr == 'properties' and 'properties' in target:
                attrvalue = merge_properties(target['properties'], attrvalue)
                target['properties'] = attrvalue

            elif attr == 'items' and 'items' in target:
                target['items'] = merge_items(target['items'], attrvalue)

            elif attr == 'required' and 'required' in target:
                res = set(target['required'])
                res.update(attrvalue)
                target['required'] = sorted(res)

            else:
                target.setdefault(attr, attrvalue)
    return target


def merge_properties(target, definition):
    for attr, schema in definition.items():
        try:
            src = target[attr]
            merge_schemas(src, schema)
        except KeyError:
            target.setdefault(attr, schema)
    return target


def merge_items(target, definition):
    if target is None:
        return definition
    if isinstance(target, dict):
        return merge_schemas(target, definition)
    raise NotImplementedError
