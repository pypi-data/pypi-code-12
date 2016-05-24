# -*- coding: utf-8 -*-
from congo.maintenance import get_site_model
from django import shortcuts
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from urlparse import urlparse, parse_qsl, urlunparse
import os

def change_site_membership(modeladmin, request, queryset):
    title = _("Change site membership")
    action = "change_site_membership"

    model = get_site_model()
    sites = model.objects.all()
    object_id_set = ','.join([str(obj.id) for obj in queryset])

    extra_context = {
        "title": title,
        "action": action,
        "sites": sites,
        "object_id_set": object_id_set,
    }

    # @OG change to 'admin/actions/%s.html' % action
    return shortcuts.render(request, 'admin/action_form.html', extra_context)
change_site_membership.short_description = _("Change site membership")

def change_site_membership_action(modeladmin, request):
    try:
        model = modeladmin.queryset(request).model
        object_id_set = request.POST.get('object_id_set')
        objects = model.objects.filter(id__in = object_id_set.split(','))
        site_id_list = request.POST.getlist('sites')
        sites = get_site_model().objects.filter(id__in = site_id_list)
        clear = 'clear' in request.POST

        rows_updated = 0

        for o in objects:
            if hasattr(o, 'sites'):
                if clear:
                    o.sites.clear()
                for s in sites:
                    o.sites.add(s)
            else:
                try:
                    o.site = sites[0]
                except IndexError:
                    o.site = None
            rows_updated += 1

        messages.success(request, _("Site membership was changed: %s") % rows_updated)
    except AttributeError:
        pass

    return HttpResponseRedirect(request.POST.get('next', '..'))

def change_date_range(modeladmin, request, queryset):
    rows_updated = queryset.update(start_date = '2000-01-01', end_date = '2099-01-01')
    modeladmin.message_user(request, _("Date range changed: %s") % rows_updated)
change_date_range.short_description = _("Change the date range for 100 years")

def make_visible(modeladmin, request, queryset):
    rows_updated = queryset.update(is_visible = True)
    modeladmin.message_user(request, _("Changed to visible: %s") % rows_updated)
make_visible.short_description = _("Change selected to visible")

def make_invisible(modeladmin, request, queryset):
    rows_updated = queryset.update(is_visible = False)
    modeladmin.message_user(request, _("Changed to invisible: %s") % rows_updated)
make_invisible.short_description = _("Change selected to invisible")

def make_active(modeladmin, request, queryset):
    rows_updated = queryset.update(is_active = True)
    modeladmin.message_user(request, _("Changed to active: %s") % rows_updated)
make_active.short_description = _("Change selected to active")

def make_inactive(modeladmin, request, queryset):
    rows_updated = queryset.update(is_active = False)
    modeladmin.message_user(request, _("Changed to inactive: %s") % rows_updated)
make_inactive.short_description = _("Change selected to inactive")

def show_on_screen(modeladmin, request, queryset):
    rows_updated = queryset.update(is_on_screen = True)
    modeladmin.message_user(request, _("Shown on screen: %s") % rows_updated)
show_on_screen.short_description = _("Show on screen")

def hide_from_screen(modeladmin, request, queryset):
    rows_updated = queryset.update(is_on_screen = False)
    modeladmin.message_user(request, _("Hidden from screen: %s") % rows_updated)
hide_from_screen.short_description = _("Hide from screen")

#def clear_related_objects_cache(modeladmin, request, queryset):
#    for obj in queryset:
#        RelatedContent.clear_related_objects_cache_for_object(obj)
#    modeladmin.message_user(request, "Wyczyszczono cache powiązanych obiektów")
#clear_related_objects_cache.short_description = "Wyczyść cache powiązanych obiektów"

#def auto_translate(modeladmin, request, queryset):
#    if hasattr(modeladmin, 'prepopulated_fields'):
#        prepopulated_fields = getattr(modeladmin, 'prepopulated_fields')
#    else:
#        prepopulated_fields = {}
#
#    for obj in queryset:
#        obj.auto_translate(prepopulated_fields = prepopulated_fields)
#        obj.save()
#        modeladmin.message_user(request, """Pola obiektu "%s" zostały przetłumaczone""" % obj)
#auto_translate.short_description = "Tłumacz pola obiektu"

#def model_to_xml(modeladmin, request, queryset):
#    fields = getattr(modeladmin, 'xml_fields')
#
#    if fields:
#        for obj in queryset:
#            xml = model_to_xml_(obj, fields)
#            content_type = ContentType.objects.get_for_model(obj)
#
#            slug = getattr(obj, 'slug', slugify(unicode(obj)))
#
#            filename = "%s_%s_%s.xml" % (content_type.app_label, content_type.model, slug)
#            file_path = os.path.join(settings.TEMP_ROOT, 'xml', filename)
#
#            f = open(file_path, 'w')
#            f.write(xml)
#            f.close()
#
#            modeladmin.message_user(request, """Obiekt "%s" został wyeksportowany do XML""" % obj)
#    else:
#        modeladmin.message_user(request, "Nie określono pól do eksportu", level = messages.ERROR)
#model_to_xml.short_description = "Eksportuj do XML"
