#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

from ishtar_common.data_importer import *

from archaeological_context_records import models


class ContextRecordsImporterBibracte(Importer):
    DESC = u"Exports Bibracte : importeur pour l'onglet UE"
    OBJECT_CLS = models.ContextRecord
    DEFAULTS = {}
    LINE_FORMAT = [
        # ID operation
        ImportFormater('operation__operation_code', IntegerFormater(),
                       duplicate_fields=[('parcel__operation__operation_code',
                                          False)]),
        # ID UE
        ImportFormater('external_id', UnicodeFormater(120),
                       duplicate_fields=[('label', False)],),
        # Type
        ImportFormater('unit', TypeFormater(models.Unit), required=False),
        # description
        ImportFormater('description', UnicodeFormater(1000), required=False,),
        # interprétation
        ImportFormater('interpretation', UnicodeFormater(1000),
                       required=False,),
        # date ouverture
        ImportFormater('opening_date', DateFormater(['%Y/%m/%d']),
                       required=False,),
        # date fermeture
        ImportFormater('closing_date', DateFormater(['%Y/%m/%d']),
                       required=False,),
        # lien vers parcelle
        ImportFormater('parcel__external_id', UnicodeFormater(12),
                       required=False,),
        # lien vers ID sig
        None,
        # commentaire
        ImportFormater('comment', UnicodeFormater(1000), required=False,),
        # ????
        None,
        # chrono #TODO! pas de vrai création de nouvelle et en cas de modif
        # c'est la zone
        ImportFormater('datings__period', TypeFormater(models.Period),
                       required=False),
    ]


class ContextRecordsRelationImporterBibracte(Importer):
    DESC = u"Exports Bibracte : importeur pour l'onglet relations entre UE"
    OBJECT_CLS = models.RecordRelations
    DEFAULTS = {}
    LINE_FORMAT = [
        # code OA
        ImportFormater(
            'left_record__operation__operation_code', IntegerFormater(),
            duplicate_fields=[('right_record__operation__operation_code',
                               False)],),
        # identifiant UE 1
        ImportFormater('left_record__external_id', UnicodeFormater(120),),
        # type relation
        ImportFormater('relation_type', TypeFormater(models.RelationType),),
        # identifiant UE 2
        ImportFormater('right_record__external_id', UnicodeFormater(120),),
    ]
