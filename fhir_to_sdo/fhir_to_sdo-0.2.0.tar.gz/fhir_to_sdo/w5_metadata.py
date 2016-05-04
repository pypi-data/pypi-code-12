# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import logging
from rdflib import Graph, RDF, RDFS, Namespace, URIRef
from typing import Optional, List

FHIR = Namespace("http://hl7.org/fhir/")
SDO = Namespace("http://schema.org/")
# We need to examine why we can't say "fhir.schema.org" below
FHIR_SDO = Namespace("http://schema.org/")


class W5Entry:
    def __init__(self, g: Graph, uri: URIRef, parentns: str, parent: Optional[URIRef]) -> None:
        self.name = W5Entry._name(str(uri))
        self.fhir_uri = FHIR_SDO[self.name]
        self.parent_ns = parentns
        if parent:
            self.parent_name = W5Entry._name(str(parent))
            self.parent_uri = FHIR_SDO[self.parent_name]
            self.description = g.value(uri, RDFS.comment, default="NO DESCRIPTION")
        else:
            root, ident = str(uri).split('w5#')
            self.parent_name, ext = ident.split('.')
            self.parent_uri = FHIR_SDO[self.parent_name]
            parent = URIRef(root + 'w5#' + self.parent_name)
            parent_desc = g.value(parent, RDFS.comment, default="NO DESCRIPTION")
            self.description = ext.title() + ' ' + parent_desc

    def sdo_class(self):
        return """<div typeof="rdfs:Class" resource="%(fhir_uri)s">
  <span class="h" property="rdfs:label">w5:%(name)s</span>
  <span property="rdfs:comment">%(description)s</span>
  <span>Subclass of: <a property="rdfs:subClassOf" href="%(parent_uri)s">%(parent_ns)s%(parent_name)s</a></span>
  <link property="http://schema.org/isPartOf" href="http://w5.schema.org" />
</div>""" % self.__dict__

    @staticmethod
    def _name(uri: str) -> str:
        return uri.split('#')[1] if '#' in uri else uri.rsplit('/', 1)[1]


class W5Metadata:
    def __init__(self, metadata_file_loc: str) -> None:
        logging.info("Reading fhir.ttl metatdata file")
        self.graph = Graph()
        self.graph.parse(metadata_file_loc, format='turtle')

    def as_sdo(self) -> List[W5Entry]:
        # Start with the root w5 node
        w5array = [W5Entry(self.graph, FHIR.w5, '', SDO.Thing)]

        # Cover all the immediate descendants
        fhir_subjs = set(self.graph.transitive_subjects(RDFS.subClassOf, FHIR.w5))
        w5array += [W5Entry(self.graph, e, 'w5:', FHIR.w5) for e in fhir_subjs if e != FHIR.w5]

        # Traverse all the different sorts of things that have a FHIR.w5 predicate
        # (Curiously, w5 is both a Class and a Property...)
        for defn in set(self.graph.objects(None, FHIR.w5)):     # Gives us a BNode
            for o in self.graph.objects(defn, RDF.type):        # Access the w5 types
                if o not in fhir_subjs:
                    fhir_subjs.add(o)
                    w5array.append(W5Entry(self.graph, o, 'w5:', None))

        return w5array
