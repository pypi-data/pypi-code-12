#!/usr/bin/env python
# -*- coding: utf-8 -*-

ISHTAR_DPTS = [44, 49, 53, 72, 85]

# DB key: (txt_idx, (key, label))
ISHTAR_OPE_TYPES = {
    (u'préventive', u'BAT'):(u'building_study',
                             u"Étude de bâti (préventif)"),
    (u'programmée', u'BAT'):(u'building_study_research',
                             u"Étude de bâti (programmé)"),
    (u'préventive', u'DIAG'):(u'arch_diagnostic',
                              u"Diagnostic archéologique (préventif)"),
    (u'programmée', u'DIAG'):(u'arch_diagnostic_research',
                              u"Diagnostic archéologique (programmé)"),
    (u'préventive', u'ED'):(u'documents_study',
                            u'Étude documentaire (préventif)'),
    (u'programmée', u'ED'):(u'documents_study_research',
                            u'Étude documentaire (programmé)'),
    (u'préventive', u'EV'):(u'evaluation',
                            u'Évaluation'),
    (u'préventive', u'Fo. Prév.'):(u'prev_excavation',
                                   u"Fouille archéologique préventive"),
    (u'préventive', u'FO'):(u'prev_excavation',
                            u"Fouille archéologique préventive"),
    (u'programmée', u'FO'):(u'prog_excavation',
                            u"Fouille archéologique programmée"),
    (u'programmée', u'FP'):(u'prog_excavation',
                            u"Fouille archéologique programmée"),
    (u'programmée', u'FPP'):(u'prog_excavation',
                             u"Fouille archéologique programmée pluriannuelle"),
    (u'programmée', u'PA'):(u'aerial_survey_research',
                            u"Prospection aérienne (programmée)"),
    (u'préventive', u'PA'):(u'aerial_survey',
                            u"Prospection aérienne (préventif)"),
    (u'programmée', u'PCR'):(u"collective_research_project",
                             u"Projet Collectif de Recherche"),
    (u'programmée', u'PI'):(u'inventory_survey_research',
                            u"Prospection inventaire (programmé)"),
    (u'préventive', u'PI'):(u'inventory_survey',
                            u"Prospection inventaire (préventif)"),
    (u'programmée', u'PR'):(u'survey_research',
                            u"Prospection (programmé)"),
    (u'préventive', u'PR'):(u'survey',
                            u"Prospection (préventif)"),
    (u'programmée', u'PT'):(u'thematic_survey',
                            u"Prospection thématique"),
    (u'programmée', u'RE'):(u'rock_art_survey',
                            u"Prospection avec relevé d'art rupestre"),
    (u'préventive', u'SD'):(u'sampling',
                            u"Sondage (programmé)"),
    (u'programmée', u'SD'):(u'sampling_research',
                            u"Sondage (préventif)"),
    (u'préventive', u'SP'):(u'prev_excavation',
                            u"Fouille archéologique préventive"),
    (u'préventive', u'SU'):(u'emergency_excavation',
                            u"Sauvetage urgent"),
}

ISHTAR_PERIODS = {
    u'MA':u'middle_age',
    u'IND':u'indetermined',
    u'CON':u'contemporan',
    u'MOD':u'modern',
    u'REC':u'recent_times',
    u'BMA':u'low_middle_age',
    u'MAC':u'classic_middle_age',
    u'HMA':u'high_middle_age',
    u'BAS':u'low_empire',
    u'HAU':u'high-empire',
    u'NRE':u'republic',
    u'GAL':u'gallo-roman',
    u'FE2':u'second_iron_age',
    u'FE1':u'first_iron_age',
    u'BRF':u'final_bronze_age',
    u'BRM':u'middle_bronze_age',
    u'BRA':u'old_bronze_age',
    u'FER':u'iron_age',
    u'BRO':u'bronze_age',
    u'PRO':u'protohistory',
    u'NEF':u'final_neolithic',
    u'NER':u'recent_neolithic',
    u'NEM':u'middle_neolithic',
    u'NEA':u'old_neolithic',
    u'NEO':u'neolithic',
    u'MER':u'recent_mesolithic',
    u'MEM':u'middle_mesolithic',
    u'MEA':u'old_mesolithic',
    u'MES':u'mesolithic',
    u'PAF':u'final_paleolithic',
    u'PAS':u'late_paleolithic',
    u'PAM':u'middle_paleolithic',
    u'PAA':u'ancien_paleolithic',
    u'PAL':u'paleolithic',
    u'':u'not_yet_documented',
}

ISHTAR_PERMIT_TYPES = {
    '':(u"NP", 'Non précisé'),
    u'permis de démolir':(u"PD", u"Permis de démolir"),
    u"autorisation":(u"AUT", u"Autorisation"),
    u"étude d'impact":(u"EI", u"Étude d'impact"),
    u"certificat d'urbanisme":(u"CU", u"Certificat d'urbanisme"),
    u'installation classée':(u"IC", u'Installation classée'),
    u'permis de construire':(u"PC", u'Permis de construire'),
    u'découverte fortuite':(u"DF", u"Découvert fortuite"),
    u'autre':(u"O", u"Autre"),
    u'autorisation de travaux':(u"AT", u"Autorisation de travaux"),
    u'autorisation de lotir':(u"AL", u"Autorisation de lotir"),
    u'étude préalable MH':(u"EMH", u"Étude préalable MH")
}

ISHTAR_DOC_TYPES = {
    'RF':u"Rapport final",
    'RI':u"Rapport intermédiaire",
    "undefined":u"Non précisé"
}

# attrs, convert[, relative col number, multi]
ISHTAR_OPE_COL_FORMAT = [
 [('code_patriarche',), 'parse_string'],
 None, # pass
 None, # pass
 None, # pass
 [('code_dracar',), 'parse_string_10'],
 None, # pass
 (('in_charge',), 'parse_name_surname'),
 None, # organisation - valeur par défaut si pas precise en colonne "V"
 (('common_name',), 'parse_ope_name'), # Nom générique
 (('periods',), 'parse_period_name', None, True),
 (('cira_rapporteur',), 'parse_name_surname'),
 (('operation_type',), 'parse_patriarche_operationtype'),
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # commentaire adresse - géré en colonne S
 None, # pass
 (('comment',), 'parse_comment_addr_nature', [16]),
 None, #  (('associated_file', 'permit_type'), 'parse_permittype'),
 None, #  (('associated_file', 'internal_reference'), 'parse_fileref'),
 (('in_charge__attached_to',), 'parse_orga', [7]),
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 (('start_date',), 'parse_date'),
 None, # pass
 None, # pass
 (('negative_result',), 'parse_bool'),
 None, # pass
 None, #  (('associated_file', 'year'), 'parse_yearref'),
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 (('year',), 'parse_yearref'),
 None, # pass
 (('administrative_act', 'signature_date',), 'parse_date'),
 (('cira_date',), 'parse_date'),
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 (('end_date',), 'parse_date'),
 None, # pass
 None, # pass
 None, # act_type
 (('administrative_act', 'act_type'), 'parse_admin_act_typ', [49]),
 (('administrative_act', 'ref_sra'), 'parse_fileref'),
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 None, # pass
 (('surface',), 'parse_ha'),
 None, # pass
 (('source', 'index'), 'parse_rapp_index'),
 (('source', 'reference'), 'parse_string'),
 None, # pass
 None, # pass
 (('source', 'internal_reference'), 'parse_string'),
 (('source', 'receipt_date'), 'parse_date'),
 None, # pass
 None, # pass
 (('source', 'source_type'), 'parse_doc_types'),
 None, # pass
 None, # pass
 None, # pass
 (('towns',), 'parse_insee', None, True),
 None, # pass
 (('parcels',), 'parse_parcels', [79]),
 None, # pass
 None, # pass
 None, # pass
 (('eas_number',), 'parse_string'),
 None, # pass
 (('source', 'title'), 'parse_string'),
 None, # pass
 None, # pass
]

