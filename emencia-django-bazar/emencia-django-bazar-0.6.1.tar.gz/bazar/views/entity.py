# -*- coding: utf-8 -*-
"""
Entity views
"""
from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from braces.views import LoginRequiredMixin

from bazar.models import ATTACHMENTS_WITH_SENDFILE, Entity, Note
from bazar.forms.entity import EntityForm, EntityForKindForm, EntityDeleteForm
from bazar.utils.mixins import KindMixin, EntityMixin
from bazar.utils.views import ListAppendView


class EntityIndexView(LoginRequiredMixin, ListAppendView):
    """
    Entity Index view, all kind mixed
    """
    model = Entity
    form_class = EntityForm
    template_name = "bazar/entity/index.html"
    paginate_by = settings.BAZAR_ENTITY_INDEX_PAGINATE
    
    def annotate_notes(self, queryset):
        return queryset.annotate(num_notes=Count('note'))
    
    def get_queryset(self):
        return self.annotate_notes(super(EntityIndexView, self).get_queryset())

    def get_success_url(self):
        return reverse('bazar:entity-index')
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('New entity has been created'), fail_silently=True)
        return super(EntityIndexView, self).form_valid(form)


class KindEntityIndexView(KindMixin, EntityIndexView):
    """
    Entity index view for a given kind
    """
    model = Entity
    form_class = EntityForKindForm
    template_name = "bazar/entity/index.html"
    paginate_by = settings.BAZAR_ENTITY_INDEX_PAGINATE
    
    def get_queryset(self):
        q = super(EntityIndexView, self).get_queryset()
        return self.annotate_notes(q.filter(kind=self.get_kind()))

    def get_form_kwargs(self):
        kwargs = super(KindEntityIndexView, self).get_form_kwargs()
        kwargs.update({'kind': self.get_kind()})
        return kwargs

    def get_success_url(self):
        return reverse('bazar:entity-for-kind-index', args=(self.get_kind(),))


class EntityDetailView(LoginRequiredMixin, EntityMixin, generic.DetailView):
    """
    Entity detail view
    """
    model = Entity
    template_name = "bazar/entity/detail.html"
    context_object_name = "entity_instance"
    
    def get_object(self, queryset=None):
        return self.get_entity()
    
    def get_notes(self):
        return self.object.note_set.all().order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super(EntityDetailView, self).get_context_data(**kwargs)
        context.update({
            'ATTACHMENTS_WITH_SENDFILE': ATTACHMENTS_WITH_SENDFILE,
        })
        return context
    

class EntityEditView(LoginRequiredMixin, EntityMixin, generic.UpdateView):
    """
    Entity edit view
    """
    model = Entity
    form_class = EntityForm
    template_name = 'bazar/entity/form.html'
    context_object_name = "entity_instance"
    
    def get_object(self, queryset=None):
        return self.get_entity()

    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Entity has been edited successfully'), fail_silently=True)
        return super(EntityEditView, self).form_valid(form)


class EntityDeleteView(LoginRequiredMixin, EntityMixin, generic.UpdateView):
    """
    Entity delete view
    """
    model = Entity
    form_class = EntityDeleteForm
    template_name = 'bazar/note/delete_form.html'
    context_object_name = "entity_instance"
    
    def get_object(self, queryset=None):
        entity = self.get_entity()
        self.memoized_entity = {
            'name': entity.name,
            'kind': entity.kind,
            'kind_display': entity.get_kind_display(),
        }
        return entity

    def get_success_url(self):
        """
        TODO: IF move_notecards_to has been used, go to the targeted entity details
              ELSE go to kind index?
        """
        return reverse('bazar:entity-index')
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _("Entity '{name}' has been deleted".format(name=self.memoized_entity['name'])), fail_silently=True)
        return super(EntityDeleteView, self).form_valid(form)
