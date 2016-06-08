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

from django.utils.translation import ugettext_lazy as _

from archaeological_files_pdl.wizards import FileWizard, FileModificationWizard
from archaeological_operations.wizards import is_preventive, is_not_preventive

from ishtar_common.views import OrganizationPersonCreate, \
    OrganizationPersonEdit

from archaeological_files_pdl import forms
from archaeological_files import forms as ref_forms
from archaeological_operations.forms import ParcelFormSet

from archaeological_files import models


file_creation_wizard_is_preventive = is_preventive(
    'general-file_creation', models.FileType, type_key='file_type')
file_creation_wizard_is_not_preventive = is_not_preventive(
    'general-file_creation', models.FileType, type_key='file_type')
file_creation_wizard = FileWizard.as_view([
    ('general-file_creation', forms.FileFormGeneral),
    ('preventivetype-file_creation', forms.FileFormPreventiveType),
    ('preventiveplanning-file_creation', forms.FileFormPlanning),
    ('researchaddress-file_creation', forms.FileFormResearchAddress),
    ('parcelspdl-file_creation', ParcelFormSet),
    ('generalcontractor-file_creation', forms.FileFormGeneralContractor),
    ('planningservice-file_creation', forms.FileFormPlanningService),
    ('research-file_creation', ref_forms.FileFormResearch),
    ('instruction-file_creation', forms.FileFormInstruction),
    ('final-file_creation', ref_forms.FinalForm)],
    label=_(u"New file"),
    condition_dict={
        'preventivetype-file_creation': file_creation_wizard_is_preventive,
        'preventiveplanning-file_creation': file_creation_wizard_is_preventive,
        'generalcontractor-file_creation': file_creation_wizard_is_preventive,
        'planningservice-file_creation': file_creation_wizard_is_preventive,
        'researchaddress-file_creation':
        file_creation_wizard_is_not_preventive,
        'research-file_creation': file_creation_wizard_is_not_preventive},
    url_name='file_creation',)

file_modification_wizard_is_preventive = is_preventive(
    'general-file_modification', models.FileType, type_key='file_type')
file_modification_wizard_is_not_preventive = is_not_preventive(
    'general-file_modification', models.FileType, type_key='file_type')
file_modification_wizard = FileModificationWizard.as_view([
    ('selec-file_modification', ref_forms.FileFormSelection),
    ('general-file_modification', forms.FileFormGeneral),
    ('preventivetype-file_modification', forms.FileFormPreventiveType),
    ('preventiveplanning-file_modification', forms.FileFormPlanning),
    ('researchaddress-file_modification', forms.FileFormResearchAddress),
    ('parcelspdl-file_modification', ParcelFormSet),
    ('generalcontractor-file_modification', forms.FileFormGeneralContractor),
    ('planningservice-file_modification', forms.FileFormPlanningService),
    ('research-file_modification', ref_forms.FileFormResearch),
    ('instruction-file_modification', forms.FileFormInstructionEdit),
    ('final-file_modification', ref_forms.FinalForm)],
    label=_(u"File modification"),
    condition_dict={
    'preventivetype-file_modification': file_modification_wizard_is_preventive,
    'preventiveplanning-file_modification':
    file_modification_wizard_is_preventive,
    'generalcontractor-file_modification':
    file_modification_wizard_is_preventive,
    'planningservice-file_modification':
    file_modification_wizard_is_preventive,
    'researchaddress-file_modification':
    file_modification_wizard_is_not_preventive,
    'research-file_modification': file_modification_wizard_is_not_preventive},
    url_name='file_modification',)


class TownPlanningEdit(OrganizationPersonEdit):
    relative_label = _("File followed by")


class TownPlanningCreate(OrganizationPersonCreate):
    relative_label = _("File followed by")
