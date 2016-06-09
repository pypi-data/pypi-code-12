#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

from django.utils.translation import ugettext_lazy as _
from django.db.models import *
from django.contrib.contenttypes.models import ContentType
import unicodedata


def getFieldVerboseName(qs, field):
    try:
        # Find qs non related model fields
        if '__' not in field:
            return _(qs.model._meta.get_field(field).verbose_name)

        # Find the related model field
        else:
            if '__id' in field:
                field = field.replace('__id', '')
            else:
                related_model, field = field.split('__')[-2], field.split('__')[-1]
        try:
            return _(qs.model._meta.get_field(related_model).rel.to._meta.get_field(field).verbose_name)
        except:
            ct = ContentType.objects.get(model=related_model)
            return get_model(ct.app_label, ct.model)._meta.get_field(field).verbose_name
    except:
        return field.replace('_', ' ').capitalize()


# Gets the translation of a field or related field name
def getFieldType(qs, field):
    try:
        # Find qs non related model fields
        if '__' not in field:
            return _(qs.model._meta.get_field(field).get_internal_type())
        # Find the related model field
        else:
            if '__id' in field:
                field = field.replace('__id', '')
            else:
                related_model, field = field.split('__')[-2], field.split('__')[-1]
        try:
            return _(qs.model._meta.get_field(related_model).rel.to._meta.get_field(field).get_internal_type())
        except:
            ct = ContentType.objects.get(model=related_model)
            return get_model(ct.app_label, ct.model)._meta.get_field(field).get_internal_type()
    except:
        return field.replace('_', ' ').capitalize()


def mergePerson(queryset, request_data, config):
    if config == 'Client':
        type_id = 'client_type_id'
        type_id_in = 'client_type_id__in'
        person = 'Client'
        person_group = 'Client Group'
        pg = 'cg_'
        p = 'c_'
    elif config == 'ClientEntry':
        type_id = 'cliententry_type_id'
        type_id_in = 'cliententry_type_id__in'
        person = 'Client'
        person_group = 'Client Group'
        pg = 'cg_'
        p = 'c_'
    elif config == 'ClientEntry':
        type_id = 'cliententry_type_id'
        type_id_in = 'cliententry_type_id__in'
        person = 'Client'
        person_group = 'Client Group'
        pg = 'cg_'
        p = 'c_'
    elif config == 'Provider':
        type_id = 'provider_type_id'
        type_id_in = 'provider_type_id__in'
        person = 'Provider'
        person_group = 'Provider Group'
        pg = 'pg_'
        p = 'p_'
    elif config == 'ProviderPayout':
        type_id = 'providerpayout_type_id'
        type_id_in = 'providerpayout_type_id__in'
        person = 'Provider'
        person_group = 'Provider Group'
        pg = 'pg_'
        p = 'p_'
    else:
        return queryset, request_data

    if type_id in request_data:
        if request_data[type_id][1] != 'NULL':
            list_person_invoice = []
            list_persongroup_invoice = []
            if request_data[type_id][0] == type_id:
                request_data[type_id] = (unicode(type_id_in), [request_data[type_id][1]])
            if request_data[type_id][0] == type_id_in:
                for i in range(0, len(request_data[type_id][1])):
                    if type(request_data[type_id][1][i]) == unicode:
                        item_client = unicodedata.normalize('NFKD', request_data[type_id][1][i]).encode('ascii', 'ignore')
                    else:
                        item_client = request_data[type_id][1][i]

                    if pg in item_client:
                        request_data[type_id][1][i] = request_data[type_id][1][i].replace(pg, '')
                        list_persongroup_invoice.append(request_data[type_id][1][i])

                    if p in item_client:
                        request_data[type_id][1][i] = request_data[type_id][1][i].replace(p, '')
                        list_person_invoice.append(request_data[type_id][1][i])

                # del request_data[type_id]

                if config == 'Client':
                    queryset = queryset.filter(Q(client_type_id__in=list_person_invoice, client_contenttype__name=person) | Q(client_type_id__in=list_persongroup_invoice, client_contenttype__name=person_group))
                elif config == 'ClientEntry':
                    queryset = queryset.filter(Q(cliententry_type_id__in=list_person_invoice, cliententry_contenttype__name=person) | Q(cliententry_type_id__in=list_persongroup_invoice, cliententry_contenttype__name=person_group))
                elif config == 'Provider':
                    queryset = queryset.filter(Q(provider_type_id__in=list_person_invoice, provider_contenttype__name=person) | Q(provider_type_id__in=list_persongroup_invoice, provider_contenttype__name=person_group))
                elif config == 'ProviderPayout':
                    queryset = queryset.filter(Q(providerpayout_type_id__in=list_person_invoice, providerpayout_contenttype__name=person) | Q(providerpayout_type_id__in=list_persongroup_invoice, providerpayout_contenttype__name=person_group))
                else:
                    pass

    return queryset, request_data
