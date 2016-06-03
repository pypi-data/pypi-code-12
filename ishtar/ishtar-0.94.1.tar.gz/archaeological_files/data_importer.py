#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import datetime
import unicodecsv

from django.conf import settings

from ishtar_common.data_importer import *
from ishtar_common.models import Person, OrganizationType

from archaeological_operations.data_importer import *

from archaeological_files import models


class ImportClosingFormater(ImportFormater):
    def post_process(self, obj, context, value, owner=None):
        value = self.formater.format(value)
        if not value:
            return
        open_date = obj.reception_date or obj.creation_date
        if not open_date:
            return
        obj.end_date = open_date + datetime.timedelta(30)
        obj.save()


class ImportMayorFormater(ImportFormater):
    def post_process(self, obj, context, value, owner=None):
        value = self.formater.format(value)
        if type(self.field_name) in (list, tuple):
            return  # not managed
        associated_obj = get_object_from_path(obj, self.field_name)
        if not value or not obj.main_town or not associated_obj:
            return
        if slugify(value).endswith('le-maire'):
            value += u" de " + obj.main_town.name
            value = value[:300]
        setattr(associated_obj, self.field_name.split('__')[-1], value)
        associated_obj.save()


class FilePostProcessing(object):
    def post_processing(self, item, data):
        if not item.end_date:  # auto-close
            open_date = item.reception_date or item.creation_date
            if open_date:
                item.end_date = open_date + datetime.timedelta(30)
        item.save()
        return item


class FileImporterSraPdL(FilePostProcessing, Importer):
    DESC = u"Exports dossiers SRA PdL : importeur Filemaker dossiers"
    SLUG = "sra-pdl-files"
    LINE_FORMAT = []
    OBJECT_CLS = models.File
    UNICITY_KEYS = ['external_id']
    DEFAULTS = {
        ('responsible_town_planning_service', 'attached_to'): {
            'organization_type': OrganizationType.objects.get(
                txt_idx="planning_service")},
        ('general_contractor', 'attached_to'): {
            'organization_type': OrganizationType.objects.get(
                txt_idx="general_contractor")},
        tuple(): {
            'file_type': models.FileType.objects.get(
                txt_idx='preventive'),
            'creation_date': datetime.datetime.now,
        },
        ('in_charge',): {'attached_to': None},  # initialized in __init__
    }

    def _init_line_format(self):
        tf = TownFormater()
        tf.town_dct_init()
        self.line_format = [
            None,  # A, 1
            ImportFormater(
                ['general_contractor__attached_to__address',  # B, 2
                 'general_contractor__attached_to__postal_code',
                 'general_contractor__attached_to__town'],
                [UnicodeFormater(500, clean=True),
                 UnicodeFormater(5, re_filter=RE_CD_POSTAL_FILTER),
                 UnicodeFormater(70, clean=True), ],
                regexp=RE_ADD_CD_POSTAL_TOWN,
                regexp_formater_args=[[0], [1], [2]], required=False,
                comment=u"Aménageur - adresse"),
            ImportMayorFormater(
                # C, 3 TODO - extraire nom_prenom_titre
                'general_contractor__raw_name',
                UnicodeFormater(200),
                comment=u"Aménageur - nom brut",
                post_processing=True,
                required=False),
            None,  # D, 4
            ImportFormater(
                "general_contractor__title",  # E, 5
                StrChoiceFormater(Person.TYPE, cli=True),
                required=False,
                comment=u"Aménageur - titre"),
            None,  # F, 6
            None,  # G, 7
            None,  # H, 8
            ImportFormater("parcels__year",  # I, 9
                           YearNoFuturFormater(),
                           required=False),
            # J, 10
            ImportParcelFormater('', required=False, post_processing=True),
            None,  # K, 11
            ImportFormater([['main_town', 'parcels__town']],  # L, 12
                           tf,
                           required=False,
                           comment=u"Commune (si non définie avant)"),
            ImportFormater([['main_town', 'parcels__town']],  # M, 13
                           tf,
                           required=False,
                           comment=u"Commune (si non définie avant)"),
            ImportFormater('saisine_type',  # N, 14
                           TypeFormater(models.SaisineType),
                           required=False,
                           comment=u"Type de saisine"),
            None,  # O, 15
            ImportFormater('name',  # P, 16
                           UnicodeFormater(),
                           comment=u"Nom du dossier",
                           required=False),
            None,  # Q, 17
            ImportFormater(
                [
                    'responsible_town_planning_service__raw_name',
                    # R, 18 service instructeur
                    'responsible_town_planning_service__attached_to__address',
                    'responsible_town_planning_service__'
                    'attached_to__postal_code',
                    'responsible_town_planning_service__attached_to__town'],
                [UnicodeFormater(300, clean=True),
                 UnicodeFormater(300, clean=True),
                 UnicodeFormater(5, re_filter=RE_CD_POSTAL_FILTER),
                 UnicodeFormater(70, clean=True), ],
                regexp=RE_NAME_ADD_CD_POSTAL_TOWN,
                regexp_formater_args=[[0], [1], [2], [3]],
                comment=u"Service instructeur - adresse",
                required=False),
            ImportFormater(
                'comment',  # S, 19
                UnicodeFormater(prefix=u'* Considérants : '),
                comment=u"Commentaire",
                concat=True,
                required=False),
            ImportYearFormater('reception_date',  # T, 20
                               DateFormater(['%d/%m/%Y', '%d/%m/%Y']),
                               comment=u"Date de réception",
                               required=False,
                               duplicate_fields=[['creation_date', False]]),
            None,  # U, 21
            None,  # V, 22
            None,  # W, 23
            None,  # X, 24
            None,  # Y, 25
            None,  # Z, 26
            None,  # AA, 27
            None,  # AB, 28
            None,  # AC, 29
            None,  # AD, 30
            None,  # AE, 31
            None,  # AF, 32
            None,  # AG, 33
            None,  # AH, 34
            ImportFormater('creation_date',  # AI, 35
                           DateFormater(['%d/%m/%Y', '%d/%m/%y']),
                           force_value=True,
                           comment=u"Date de création",
                           required=False,),
            None,  # AJ, 36
            ImportFormater('comment',  # AK, 37
                           UnicodeFormater(prefix=u"* Historique : "),
                           comment=u"Commentaire",
                           concat=True, required=False),
            ImportFormater('internal_reference',  # AL, 38
                           UnicodeFormater(60),
                           comment=u"Autre référence",
                           required=False),
            None,  # AM, 39
            None,  # AN, 40
            ImportFormater('comment',  # AO, 41
                           UnicodeFormater(
                               prefix=u"* Justificatif de prescription : "),
                           comment=u"Justificatif de prescription",
                           concat=True, required=False),
            ImportFormater('comment',  # AP, 42
                           UnicodeFormater(
                               prefix=u"* Justificatif d'intervention : "),
                           comment=u"Justificatif d'intervention",
                           concat=True, required=False),
            None,  # AQ, 43
            None,  # AR, 44
            None,  # AS, 45
            None,  # AT, 46
            ImportFormater('comment',  # AU, 47
                           UnicodeFormater(
                               prefix=u"* Méthodologie de l'opération : "),
                           comment=u"Méthodologie de l'opération",
                           concat=True, required=False),
            None,  # AV, 48
            ImportFormater('permit_reference',  # AW, 49
                           UnicodeFormater(300, clean=True),
                           regexp=RE_PERMIT_REFERENCE,
                           comment=u"Réf. du permis de construire",
                           required=False),
            ImportFormater('comment',  # AX, 50
                           UnicodeFormater(
                               prefix=u"* Référence de dossier aménageur : "),
                           comment=u"Référence de dossier aménageur",
                           concat=True, required=False),
            None,  # AY, 51
            None,  # AZ, 52
            ImportFormater('comment',  # BA, 53
                           UnicodeFormater(
                               prefix=u"* Numéro d'arrêté préfectoral : "),
                           comment=u"Numéro d'arrêté préfectoral",
                           concat=True, required=False),
            ImportFormater('comment',  # BB, 54
                           UnicodeFormater(
                               prefix=u"* Numéro d'arrêté SRA : "),
                           comment=u"Numéro d'arrêté SRA",
                           concat=True, required=False),
            ImportFormater('comment',  # BC, 55
                           UnicodeFormater(
                               prefix=u"* Numéro d'arrêté de "
                               u"post-diagnostic : "),
                           comment=u"Numéro d'arrêté de post-diagnostic",
                           concat=True, required=False),
            None,  # BD, 56
            ImportFormater([['main_town', 'parcels__town']],  # BE, 57
                           TownINSEEFormater(),
                           required=False,
                           comment=u"Commune (si non définie avant)"),
            ImportFormater('comment',  # BF, 58
                           UnicodeFormater(2000),
                           comment=u"Commentaire",
                           concat=True, required=False),
            None,  # BG, 59
            None,  # BH, 60
            None,  # BI, 61
            None,  # BJ, 62
            None,  # BK, 63
            None,  # BL, 64
            None,  # BM, 65
            None,  # BN, 66
            None,  # BO, 67
            None,  # BP, 68
            None,  # BQ, 69
            None,  # BR, 70
            None,  # BS, 71
            ImportFormater(  # BT, 72 nom service instructeur
                ['responsible_town_planning_service__attached_to__name', ],
                [UnicodeFormater(300, clean=True), ],
                regexp=RE_ORGA,
                comment=u"Service instructeur - nom",
                required=False),
            None,  # BU, 73
            None,  # BV, 74
            ImportFormater(
                'in_charge__raw_name',  # BW, 75 responsable
                UnicodeFormater(200),
                comment=u"Responsable - nom brut",
                required=False),
            ImportFormater('total_surface',  # BX, 76 surface totale
                           SurfaceFormater(),
                           comment=u"Surface totale",
                           required=False),
            ImportFormater('total_developed_surface',
                           # BY, 77 surface totale aménagée
                           SurfaceFormater(),
                           comment=u"Surface totale aménagée",
                           required=False),
            None,  # BZ, 78
            None,  # CA, 79
            None,  # CB, 80
            None,  # CC, 81
            None,  # CD, 82
            None,  # CE, 83
            None,  # CF, 84
            ImportFormater('permit_type',
                           TypeFormater(models.PermitType),
                           required=False,
                           comment=u"Type de permis"),  # CG, 85
            None,  # CH, 85
            ImportFormater('year',  # CI, 86
                           IntegerFormater(),
                           comment=u"Année du dossier",
                           required=True),
            ImportFormater('numeric_reference',  # CJ, 87
                           IntegerFormater(),
                           comment=u"Identifiant numérique",
                           required=True),
            ImportFormater('external_id',  # CK, 88
                           UnicodeFormater(),
                           comment=u"Identifiant externe",
                           required=True),
        ]

    def __init__(self, *args, **kwargs):
        super(FileImporterSraPdL, self).__init__(*args, **kwargs)
        self.DEFAULTS[('in_charge',)]['attached_to'], created = \
            models.Organization.objects.get_or_create(
                name='SRA Pays de la Loire',
                defaults={
                    'organization_type':
                    OrganizationType.objects.get(txt_idx='sra')})
        self._init_line_format()
        if tuple() not in self._defaults:
            self._defaults[tuple()] = {}
        self._defaults[tuple()]['history_modifier'] = self.history_modifier
        self._associate_db_target_to_formaters()


def test(filename):
    importer = FileImporterSraPdL(skip_lines=3, output='cli')
    with open(filename) as csv_file:
        encodings = [settings.ENCODING, settings.ALT_ENCODING, 'utf-8']
        for encoding in encodings:
            try:
                importer.importation(
                    [line for line in
                     unicodecsv.reader(csv_file, encoding='utf-8')])
                # importer.importation(unicode_csv_reader(
                #        [line.decode(encoding)
                #         for line in csv_file.readlines()])
                print importer.get_csv_errors()
                break
            except ImporterError, e:
                print(unicode(e))
                if e.type == ImporterError.HEADER \
                        and encoding != encodings[-1]:
                    csv_file.seek(0)
                    continue
            except UnicodeDecodeError:
                if encoding != encodings[-1]:
                    csv_file.seek(0)
                    continue
