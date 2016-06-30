# -*- coding: utf-8 -*-
# This file is part of KTBS <http://liris.cnrs.fr/sbt-dev/ktbs>
# Copyright (C) 2011-2012 Pierre-Antoine Champin <pchampin@liris.cnrs.fr> /
#    Universite de Lyon <http://www.universite-lyon.fr>
#
#    KTBS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KTBS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with KTBS.  If not, see <http://www.gnu.org/licenses/>.

"""
ActivityStreams parser/serializer.
http://tools.ietf.org/html/draft-snell-activitystreams-09
"""

from json import loads
from logging import getLogger
from rdflib import BNode, Graph, Namespace, RDF, URIRef, Literal

from rdfrest.exceptions import ParseError
from rdfrest.parsers import register_parser
from rdfrest.util.__init__ import coerce_to_uri
from ktbs.namespace import KTBS, KTBS_NS_URI

LOG = getLogger(__name__)

PREFIXES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'dctypes': 'http://purl.org/dc/dcmitype/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'vcard': 'http://www.w3.org/2006/vcard/ns#',
    'org': 'http://www.w3.org/ns/org#',
    'prov': 'http://www.w3.org/ns/prov#',
    'link': 'http://www.iana.org/assignments/link-relations/',
    # actually not specified by AS, but required by this code
    'as': 'http://activitystrea.ms/2.0/',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
}

KEYWORDS = {"id", "language", "objectType", "rel", }

AS = Namespace('http://activitystrea.ms/2.0/')

VOCAB = {
    "objectType": {
        "@id": AS.objectType,
        "@type": "@id"
    },
    "displayName": {
        "@id": AS.displayName,
        "@type": "rdf:langString",
    },
    "url": {
        "@id": AS.url,
        "@type": "@id",
    },
    "mediaType": {
        "@id": AS.mediaType,
        "@type": "xsd:string",
    },
    "verb": {
        "@id": AS.verb,
        "@type": "@vocab"
    },
    "actor": {
        "@id": AS.actor,
        "@type": "@id",
    },
    "object": {
        "@id": AS.object,
        "@type": "@id",
    },
    "target": {
        "@id": AS.target,
        "@type": "@id",
    },
    "result": {
        "@id": AS.result,
        "@type": "@id",
    },
    "instrument": {
        "@id": AS.instrument,
        "@type": "@id",
    },
    "participant": {
        "@id": AS.participant,
        "@type": "@id",
    },
    "completed": {
        "@id": AS.CompletedStatus
    },
    "active": {
        "@id": AS.ActiveStatus
    },
    "canceled": {
        "@id": AS.CanceledStatus
    },
    "pending": {
        "@id": AS.PendingStatus
    },
    "tentative": {
        "@id": AS.TentativeStatus
    },
    "to": {
        "@id": AS.to,
        "@type": "@id",
    },
    "bto": {
        "@id": AS.bto,
        "@type": "@id",
    },
    "cc": {
        "@id": AS.cc,
        "@type": "@id",
    },
    "bcc": {
        "@id": AS.bcc,
        "@type": "@id",
    },
    "alias": {
        "@id": AS.alias,
        "@type": "@id",
    },
    "author": {
        "@id": AS.author,
        "@type": "@id",
    },
    "content": {
        "@id": AS.content,
        "@type": "rdf:langString",
    },
    "duplicates": {
        "@id": AS.duplicates,
        "@type": "@id",
    },
    "icon": {
        "@id": AS.icon,
        "@type": "@id",
    },
    "image": {
        "@id": AS.image,
        "@type": "@id",
    },
    "location": {
        "@id": AS.location,
        "@type": "@id",
    },
    "published": {
        "@id": AS.published,
        "@type": "xsd:dateTime"
    },
    "generator": {
        "@id": AS.generator,
        "@type": "@id",
    },
    "provider": {
        "@id": AS.provider,
        "@type": "@id",
    },
    "summary": {
        "@id": AS.summary,
        "@type": "rdf:langString",
    },
    "updated": {
        "@id": AS.updated,
        "@type": "xsd:dateTime"
    },
    "startTime": {
        "@id": AS.startTime,
        "@type": "xsd:dateTime"
    },
    "endTime": {
        "@id": AS.endTime,
        "@type": "xsd:dateTime"
    },
    "validFrom": {
        "@id": AS.validFrom,
        "@type": "xsd:dateTime"
    },
    "validUntil": {
        "@id": AS.validUntil,
        "@type": "xsd:dateTime"
    },
    "validAfter": {
        "@id": AS.validAfter,
        "@type": "xsd:dateTime"
    },
    "validBefore": {
        "@id": AS.validBefore,
        "@type": "xsd:dateTime"
    },
    "rating": {
        "@id": AS.rating,
        "@type": "xsd:float"
    },
    "tags": {
        "@id": AS.tags,
        "@type": "@id",
    },
    "title": {
        "@id": AS.title,
        "@type": "rdf:langString",
    },
    "duration": {
        "@id": AS.duration,
        "@type": "xsd:string", # TODO better datatype? xsd:duration?
    },
    "height": {
        "@id": AS.height,
        "@type": "xsd:integer",
        # originally xsd:nonNegativeInteger, but this provides better serializations
    },
    "width": {
        "@id": AS.width,
        "@type": "xsd:integer",
        # originally xsd:nonNegativeInteger, but this provides better serializations
    },
    "inReplyTo": {
        "@id": AS.inReplyTo,
        "@type": "@id",
    },
    "actions": {
        "@id": AS.actions,
        "@type": "@id",
        "@container": "@index"
    },
    "scope": {
        "@id": AS.scope,
        "@type": "@id",
    },
    "totalItems": {
        "@id": AS.totalItems,
        "@type": "xsd:integer",
        # originally xsd:nonNegativeInteger, but this provides better serializations
    },
    "itemsPerPage": {
        "@id": AS.itemsPerPage,
        "@type": "xsd:integer",
        # originally xsd:nonNegativeInteger, but this provides better serializations
    },
    "startIndex": {
        "@id": AS.startIndex,
        "@type": "xsd:integer",
        # originally xsd:nonNegativeInteger, but this provides better serializations
    },
    "items": {
        "@id": AS.items,
        "@type": "@id",
        "@container": "@list"
    },
    "itemsAfter": {
        "@id": AS.itemsAfter,
        "@type": "xsd:dateTime"
    },
    "itemsBefore": {
        "@id": AS.itemsBefore,
        "@type": "xsd:dateTime"
    },
    "first": {
        "@id": AS.first,
        "@type": "@id",
    },
    "last": {
        "@id": AS.last,
        "@type": "@id",
    },
    "prev": {
        "@id": AS.prev,
        "@type": "@id",
    },
    "previous": {
        "@id": AS.prev,
        "@type": "@id",
    },
    "next": {
        "@id": AS.next,
        "@type": "@id",
    },
    "current": {
        "@id": AS.current,
        "@type": "@id",
    },
    "self": {
        "@id": AS.self,
        "@type": "@id",
    },
    "replies": {
        "@id": AS.replies,
        "@type": "@id",
        #"@container": "@index" # originally, but I think that's wrong
    },
    # TODO CHECK not in appendix B, but those terms are defined in 5.1 and 5.2
    # (see also OTYPE_CONVERT below)
    "activity": {
        "@id": AS.activity,
    },
    "collection": {
        "@id": AS.activity,
    },
    "post": {
        "@id": AS.post,
    },
}

@register_parser("application/activity+json", "as", 99)
def parse_activitystreams(content, base_uri=None, encoding="utf-8", graph=None):
    if graph is None:
        graph = Graph()
    if encoding.lower() != "utf-8":
        content = content.decode(encoding).encode("utf-8")
    if base_uri is None:
        base_uri = BNode()
    else:
        base_uri = coerce_to_uri(base_uri)

    data = loads(content)
    if type(data) is dict:
        data = [data]
    elif type(data) is not list:
        raise ParseError("Can only parse JSON object or array")
    add = lambda *args: graph.add(args)
    for i, elti in enumerate(data):
        if type(elti) is not dict:
            raise ParseError("Can only parse array of JSON objects")
        rel, iri = _parse_as_object(elti, add, [i], None)
        if rel is not None:
            LOG.warn("Ignoring 'rel' for top level object <%s>", iri)

    return graph

def _ctx2str(context):
    ret = ""
    for i in context:
        if type(i) == int:
            ret = "{}[{}]".format(ret, i)
        else:
            ret = "{}.{}".format(ret, i)
    return ret

def expand_key(key):
    keylst = key.split(':', 1)
    ns = PREFIXES.get(keylst[0])
    if len(keylst) == 1 or ns is None:
        None
    else:
        return URIRef(ns + keylst[1])

def _parse_as_object(obj, add, context, language):
    tobj = type(obj)
    if tobj is unicode:
        return None, URIRef(obj, PREFIXES['as'])
    elif tobj is not dict:
        raise ParseError("%s: Expected IRI or Link object"
                         .format(_ctx2str(context)))

    iri = obj.get("id")
    if iri is None:
        LOG.debug("%s: no id", _ctx2str(context))
        iri = BNode()
    else:
        iri = URIRef(iri)
    rel = obj.get("rel")
    if rel is not None:
        rel = URIRef(rel, PREFIXES['link'])
    language = obj.get("language") or language
    object_type = obj.get("ojectType")
    if object_type is not None:
        relType, object_type = _parse_as_object_list(object_type, add,
                                                     context+["objectType"],
                                                     language)
        add(iri, RDF.type, object_type)
        if relType:
            add(iri, relType, object_type)

    for key, val in obj.iteritems():
        if val is None:
            pass
        if key in KEYWORDS:
            pass
        elif key in VOCAB:
            _parse_vocab_key(iri, key, val, add, context + [key], language)
        else:
            _parse_extension_key(iri, key, val, add, context + [key], language)
    return rel, iri

def _parse_as_object_list(obj, add, context, language):
    if obj is None:
        return
    elif type(obj) is list:
        for i, elti in enumerate(obj):
            contexti = context + [i]
            yield _parse_as_object(elti, add, contexti, language)
    else:
        yield _parse_as_object(obj, add, context, language)

def _parse_vocab_key(iri, key, val, add, context, language):
    descr = VOCAB[key]
    predicate = descr['@id']
    atype = descr['@type']
    acontainer = descr.get('@container')
    tval = type(val)
    if atype == '@id':
        if acontainer is None:
            for rel, vali in _parse_as_object_list(val, add, context, language):
                add(iri, predicate, vali)
                if rel:
                    add(iri, rel, vali)
        elif acontainer == '@list':
            if tval is not list  or len(val) == 0:
                raise ParseError("{}: {} expects a non-empty list",
                                 _ctx2str(context), key)

            prevnode = iri
            prevpred = predicate
            i = 0
            for rel, vali in _parse_as_object_list(val, add, context, language):
                if rel is not None:
                    LOG.warn("{}: ignoring rel (makes no sense in this context)",
                             _ctx2str(context+[i]))
                listnode = BNode()
                add(prevnode, prevpred, listnode)
                add(listnode, RDF.first, vali)
                prevnode = listnode
                prevpred = RDF.rest
                i += 1
            add(prevnode, prevpred, RDF.nil)
        elif acontainer == '@index':
            # TODO implement @index (or maybe not?)
            # maybe not, because this is only about key 'actions' and
            # 1. it does not have much value for kTBS
            # 2. the semantics of keys is not precisely defined
            raise ParseError("{}: key {} not implemented yet",
                             _ctx2str(context), key)
        else:
            assert False, "Unimplemented @container {}".format(acontainer)

    elif atype == "rdf:langString":
        assert acontainer is None or acontainer == "@language"
        if tval is dict:
            for language, lval in val.iteritems():
                if type(language) is not unicode or type(lval) is not unicode:
                    raise ParseError("{}: ill-formed language map"
                                     .format(_ctx2str(context)))
                add(iri, predicate, Literal(lval, lang=language))
        elif tval is unicode:
            add(iri, predicate, Literal(val, lang=language))
        else:
            raise ParseError("{}: expected string or language-map"
                             .format(_ctx2str(context)))

    elif atype == "@vocab":
        assert acontainer is None
        newval = VOCAB.get(val)
        if newval is not None:
            newval = newval.get("@id")
        if newval is None:
            raise ParseError("{}: could not expand {}"
                             .format(_ctx2str(context), val))
        add(iri, predicate, newval)

    elif atype.startswith("xsd:"):
        assert acontainer is None
        if tval in (list, dict):
            raise ParseError("{}: {} expected".format(_ctx2str(context),
                                                      atype))
        else:
            val = Literal(val, datatype=expand_key(atype))
        add(iri, predicate, val)

    else:
        assert False, "Unimplemented @type {}".format(atype)

def _parse_extension_key(iri, key, val, add, context, language):
    predicate = expand_key(key)
    reli = None
    if type(val) is not list:
        val = [val]
    for i, vali in enumerate(val):
        tvali = type(vali)
        if tvali is list:
            raise ParseError(
                "%s: Can not parse embedded lists".format(
                    _ctx2str(context + [i])))
        elif tvali is dict:
            reli, vali = _parse_as_object(vali, add, context + [i],
                                          language)
            if predicate:
                add(iri, predicate, vali)
            if reli:
                add(iri, reli, vali)
        elif predicate:
            # vali could be unicode, number or bool
            add(iri, predicate, Literal(vali, lang=language))
            # NB: if number or book, lang is ignored,
            # and the correct datatype is set
    if predicate is None:
        if reli is None:
            LOG.warn("%s: ignoring unrecognized key %s",
                     _ctx2str(context[:-1]), key)
        else:
            LOG.debug("%s: unrecognized key %s, but rel was %s used instead",
                     _ctx2str(context[:-1]), key, reli)



if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    json0 = """
    {
      "totalItems": 1,
      "items" : [
        {
          "verb": "post",
          "language": "en",
          "published": "2011-02-10T15:04:55Z",
          "foo": "some extension property",
          "generator": "http://example.org/activities-app",
          "provider": "http://example.org/activity-stream",
          "displayName": {
            "en": "Martin posted a new video to his album.",
            "ga": "Martin phost le fisean nua a albam."
          },
          "actor": {
            "objectType": "person",
            "id": "urn:example:person:martin",
            "displayName": "Martin Smith",
            "url": "http://example.org/martin",
            "foo": "some other extension property",
            "image": {
              "url": "http://example.org/martin/image",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          },
          "object" : {
            "objectType": {
              "id": "http://example.org/Photo",
              "displayName": "Photo"
            },
            "id": "urn:example:album:abc123/my_fluffy_cat",
            "url": "http://example.org/album/my_fluffy_cat.jpg",
            "image": {
              "url": "http://example.org/album/my_fluffy_cat_thumb.jpg",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          },
          "target": {
            "objectType": {
              "id": "http://example.org/PhotoAlbum",
              "displayName": "Photo-Album"
            },
            "id": "urn:example.org:album:abc123",
            "url": "http://example.org/album/",
            "displayName": {
              "en": "Martin's Photo Album",
              "ga": "Grianghraif Mairtin"
            },
            "image": {
              "url": "http://example.org/album/thumbnail.jpg",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          }
        }
      ]
    }
    """
    json1 = """
    {
      "totalItems": 10,
      "next": "http://example.org/items?offset=2",
      "items" : [
        {
          "verb": "post",
          "language": "en",
          "published": "2011-02-10T15:04:55Z",
          "foo": "some extension property",
          "generator": "http://example.org/activities-app",
          "provider": "http://example.org/activity-stream",
          "displayName": {
            "en": "Martin posted a new video to his album.",
            "ga": "Martin phost le fisean nua a albam."
          },
          "actor": {
            "objectType": "person",
            "id": "urn:example:person:martin",
            "displayName": "Martin Smith",
            "url": "http://example.org/martin",
            "foo2": {
                "id": "http://example.org/foo2-object",
                "rel": "http://example.org/foo2-predicate"
            },
            "image": {
              "url": "http://example.org/martin/image",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          },
          "object" : {
            "objectType": {
              "id": "http://example.org/Photo",
              "objectType": "objectType",
              "displayName": "Photo"
            },
            "id": "urn:example:album:abc123/my_fluffy_cat",
            "url": "http://example.org/album/my_fluffy_cat.jpg",
            "image": {
              "url": "http://example.org/album/my_fluffy_cat_thumb.jpg",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          },
          "target": {
            "objectType": {
              "id": "http://example.org/PhotoAlbum",
              "displayName": "Photo-Album"
            },
            "id": "urn:example.org:album:abc123",
            "url": "http://example.org/album/",
            "displayName": {
              "en": "Martin's Photo Album",
              "ga": "Grianghraif Mairtin"
            },
            "image": {
              "url": "http://example.org/album/thumbnail.jpg",
              "mediaType": "image/jpeg",
              "width": 250,
              "height": 250
            }
          }
        },
        {
            "id": "http://example.org/another-item",
            "rel": "http://example.org/spurious-rel"
        }
      ]
    }
    """
    g = parse_activitystreams(json1)
    print g.serialize(format="n3")



