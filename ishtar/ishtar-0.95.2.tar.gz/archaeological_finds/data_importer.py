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

from archaeological_finds import models


class FindsImporterBibracte(Importer):
    DESC = u"Exports Bibracte : importeur pour l'onglet mobilier"
    OBJECT_CLS = models.BaseFind
    DEFAULTS = {}
    LINE_FORMAT = [
        # OA
        ImportFormater('context_record__operation__operation_code',
                       IntegerFormater(),),
        # external_id
        ImportFormater(
            'external_id', UnicodeFormater(120, notnull=True),
            duplicate_fields=[('find__external_id', False),
                              ('label', False),
                              ('find__label', False)]),
        # isolé ou non (si non isolé = lot)
        None,  # à corriger
        # ImportFormater(
        #     'is_isolated',
        #     StrToBoolean(choices={'lot': False, 'objet': True}),
        #     required=False),
        # ???
        None,
        # A voir
        None,
        # cf type
        None,
        # Type = sous classe de matériaux = Liste hiérarchique
        ImportFormater('find__material_types',
                       TypeFormater(models.MaterialType), required=False),
        # ???
        None,
        # lien avec contenant
        None,
        # = nombre
        ImportFormater('find__find_number', IntegerFormater(), required=False),
        # poids
        ImportFormater('find__weight', FloatFormater(), required=False),
        # unité (g par défault)
        ImportFormater('find__weight_unit',
                       StrChoiceFormater(models.WEIGHT_UNIT), required=False),
        # lien UE
        ImportFormater('context_record__external_id', UnicodeFormater(120),),
        # date decouverte
        ImportFormater('discovery_date', DateFormater(['%Y/%m/%d']),
                       required=False,),
        # lien parcelle (unique)
        None,
        # etat conservation
        ImportFormater('find__conservatory_state',
                       TypeFormater(models.ConservatoryState), required=False),
        # preservation_to_consider
        ImportFormater('find__preservation_to_considers',
                       TypeFormater(models.PreservationType), required=False),
        # comment
        ImportFormater('comment', UnicodeFormater(1000), required=False),
        # lien vers plusieurs chrono (voir gestion actuelle chrono)
        None,
        # ImportFormater('find__datings__period', TypeFormater(Period,
        #                                   many_split="&"), required=False),
        # topographic_localisation
        ImportFormater('topographic_localisation', UnicodeFormater(120),
                       required=False),
        # special_interest
        ImportFormater('special_interest', UnicodeFormater(120),
                       required=False),
        # description
        ImportFormater('description', UnicodeFormater(1000), required=False),
        # remontage
        None
    ]


class FindAltImporterBibracte(Importer):
    DESC = u"Exports Bibracte : importeur pour l'onglet prélèvement"
    OBJECT_CLS = models.BaseFind
    DEFAULTS = {}
    LINE_FORMAT = [
        # code OA
        ImportFormater('context_record__operation__operation_code',
                       IntegerFormater(),),
        # identifiant prelevement
        ImportFormater('external_id', UnicodeFormater(120, notnull=True),
                       duplicate_fields=[('find__external_id', False)]),
        # nature
        ImportFormater('find__material_types',
                       TypeFormater(models.MaterialType), required=False),
        # identifiant UE
        ImportFormater('context_record__external_id', UnicodeFormater(120),),
        # identifiant materiel
        None,
        # commentaire
        ImportFormater('comment', UnicodeFormater(1000), required=False),
    ]


class ImportTreatmentFormater(ImportFormater):
    def post_process(self, obj, context, value, owner=None):
        if obj.upstream_treatment.count():
            return
        ope_code = context['upstream_treatment'][
            'base_finds']['context_record']['operation']['operation_code']
        ope_code = int(ope_code)
        downstream = models.Find.objects.filter(
            external_id=value,
            base_finds__context_record__operation__operation_code=ope_code)
        if not downstream.count():
            return
        downstream = downstream.all()[0]
        downstream.upstream_treatment = obj
        downstream.save()
        upstream = downstream.duplicate(owner)
        upstream.downstream_treatment = obj
        upstream.save()
        return


class TreatmentImporterBibracte(Importer):
    DESC = u"Exports Bibracte : importeur pour l'onglet traitement"
    OBJECT_CLS = models.Treatment
    DEFAULTS = {}
    LINE_FORMAT = [
        # code OA
        ImportFormater(
            'upstream_treatment__base_finds__context_record__operation__'
            'operation_code',
            UnicodeFormater(120, notnull=True)),
        # identifiant
        ImportTreatmentFormater(
            'external_id',
            UnicodeFormater(120, notnull=True), post_processing=True),
        None,
        # traitement
        ImportFormater('treatment_type', TypeFormater(models.TreatmentType),),
    ]
