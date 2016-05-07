# -*- coding: utf-8 -*-
"""
Note views
"""
import os

from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from braces.views import LoginRequiredMixin

from taggit.models import Tag

from sendfile import sendfile

from bazar.models import ATTACHMENTS_WITH_SENDFILE, Entity, Note
from bazar.forms.note import NoteForm, NoteDeleteForm
from bazar.utils.mixins import MarkupMixin, EntityMixin


class NoteEntityBaseView(EntityMixin):
    """
    Base view to get the entity from note
    """
    def get_context_data(self, **kwargs):
        context = super(NoteEntityBaseView, self).get_context_data(**kwargs)
        context.update({
            'ATTACHMENTS_WITH_SENDFILE': ATTACHMENTS_WITH_SENDFILE,
            'entity_instance': self.entity,
        })
        return context
    
    def get(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteEntityBaseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteEntityBaseView, self).post(request, *args, **kwargs)


class NoteCreateView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.CreateView):
    """
    Form view to create a note for an entity
    """
    model = Note
    template_name = "bazar/note/form.html"
    form_class = NoteForm

    def get_success_url(self):
        return reverse('bazar:entity-detail', args=[self.get_kind(), self.entity.id])

    def get_form_kwargs(self):
        kwargs = super(NoteCreateView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'entity': self.entity,
        })
        return kwargs
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Note has been created'), fail_silently=True)
        return super(NoteCreateView, self).form_valid(form)


class NoteEditView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.UpdateView):
    """
    Form view to edit a note for an entity
    """
    model = Note
    template_name = "bazar/note/form.html"
    form_class = NoteForm
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])

    def get_success_url(self):
        return reverse('bazar:entity-note-detail', args=[self.get_kind(), self.entity.id, self.object.id])

    def get_context_data(self, **kwargs):
        context = super(NoteEditView, self).get_context_data(**kwargs)
        context.update({
            'note_instance': self.object,
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super(NoteEditView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'entity': self.entity,
        })
        return kwargs
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Note has been edited successfully'), fail_silently=True)
        return super(NoteEditView, self).form_valid(form)


class TagNoteListView(LoginRequiredMixin, generic.ListView):
    """
    List notes from a tag
    """
    model = Note
    template_name = "bazar/note/list.html"
    paginate_by = settings.BAZAR_NOTE_INDEX_PAGINATE
    
    def get_context_data(self, **kwargs):
        context = super(TagNoteListView, self).get_context_data(**kwargs)
        context.update({
            'ATTACHMENTS_WITH_SENDFILE': ATTACHMENTS_WITH_SENDFILE,
        })
        return context
    
    def get_tags_slug(self):
        """
        Tag slug comes from url kwargs
        """
        return self.kwargs['tag']
    
    def get_tag(self):
        """
        Getting Tag object
        """
        return get_object_or_404(Tag, slug=self.get_tags_slug())
    
    def get_queryset(self):
        return self.model.objects.select_related('entity').filter(tags__slug__in=[self.get_tags_slug()])

    def get(self, request, *args, **kwargs):
        self.tag = self.get_tag()
        return super(TagNoteListView, self).get(request, *args, **kwargs)


class NoteDetailView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.DetailView):
    """
    Note detail view
    """
    model = Entity
    template_name = "bazar/note/detail.html"
    context_object_name = "note_instance"
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])


class NoteDeleteView(LoginRequiredMixin, NoteEntityBaseView, generic.UpdateView):
    """
    Note delete view
    """
    model = Note
    form_class = NoteDeleteForm
    template_name = 'bazar/note/delete_form.html'
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])

    def get_context_data(self, **kwargs):
        context = super(NoteDeleteView, self).get_context_data(**kwargs)
        context.update({
            'note_instance': self.object,
        })
        return context

    def get_success_url(self):
        return reverse('bazar:entity-detail', args=[self.get_kind(), self.entity.id])
    
    def get(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteDeleteView, self).post(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Note has been deleted'), fail_silently=True)
        return super(NoteDeleteView, self).form_valid(form)


class AttachmentProtectedDownloadView(NoteDetailView):
    """
    View to download protected note attachment
    
    TODO: Unbind POST method for sanity
    """
    def get(self, request, **kwargs):
        self.object = self.get_object()
        
        file_path = os.path.join(settings.PROJECT_PATH, self.object.file.path)
        return sendfile(request, file_path, attachment=True, attachment_filename=os.path.basename(file_path))
