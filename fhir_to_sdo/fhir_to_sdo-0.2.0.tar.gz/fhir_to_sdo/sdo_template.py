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
#     Neither the name of the Mayo Clinic nor the names of its contributors
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

# A Schema.org template
from typing import List, Optional
from fhir_to_sdo.fhir_structured_definition import FHIRStructuredDefinition, defined_value_sets
from fhir_to_sdo.w5_metadata import W5Entry


header = """<!DOCTYPE html>
<html>
    <head>
        <title>FHIR schema</title>
        <meta charset="UTF-8" />
        <style type="text/css">
      span.h {
        padding-left: 0px;
        font-weight: bold;
      }
      span {
        display: block;
        padding-left: 10px;
      }
    </style>
    </head>
    <body>
"""

body = """
    <h1>FHIR Schema Extension </h1>
        <hr />
        <p vocab="http://schema.org" prefix="%(prefix)s http://%(base)s/">Default vocabulary prefix: '%(prefix)s'</p>
        <p> <span property="schema:softwareVersion">%(base)s Version %(version)s</span> </p>
        <hr/>
        <h2>Classes</h2>
        %(classes)s
        <h2>Properties</h2>
        %(props)s
        <h2>Value Sets</h2>
        %(valuesets)s
    </body>
</html>"""


def sdo_template(ontology: List[W5Entry], defs: Optional[List[FHIRStructuredDefinition]], version: str,
                 base: str = 'fhir.schema.org', prefix: str='fhir') -> str:
    if defs is None:
        defs = []
    classes = '\n\t'.join([ontent.sdo_class() for ontent in ontology]) + '\n\t' + \
              '\n\t'.join([fsd.sdo_class() for fsd in defs])
    props = '\n\t'.join([fsd.sdo_properties() for fsd in defs])
    valuesets = defined_value_sets.sdo_valuesets()
    return header + body % vars()
