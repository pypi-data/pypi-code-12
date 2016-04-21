from django.db import models
from pagetree.models import PageBlock, Hierarchy, Section
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django import forms
from datetime import datetime
from django.core.urlresolvers import reverse

def all_pageblocks():
    # TODO: this will break in sites with more than one hierarchy
    h = Hierarchy.objects.all()[0]
    for s in h.get_root().get_descendants():
        for p in s.pageblock_set.all():
            yield p

class ProxyBlock(models.Model):
    pageblocks = GenericRelation(PageBlock)
    proxied_block = models.ForeignKey(PageBlock,related_name="proxied_block",null=True)
    display_name = "ProxyBlock"
    exportable = False
    importable = False

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def edit_label(self):
        return "%s: %s" % (self.display_name,unicode(self.proxied_block))

    def edit_form(self):
        block_choices = [
            (b.id,"%s%s" % (b.section.get_absolute_url(),
                            b.label))
            for b in all_pageblocks()]
        class EditForm(forms.Form):
            proxied_block = forms.ChoiceField(label="Block to Proxy",
                                              choices=block_choices,
                                              initial=self.proxied_block.id,
                                              )
        return EditForm()

    @classmethod
    def add_form(self):
        block_choices = [
            (b.id,"%s%s" % (b.section.get_absolute_url(),
                            b.label))
            for b in all_pageblocks()]
        class AddForm(forms.Form):
            proxied_block = forms.ChoiceField(label="Block to Proxy",
                                              choices=block_choices)
        return AddForm()

    @classmethod
    def create(self,request):
        proxied_block = PageBlock.objects.get(id=request.POST.get('proxied_block',''))
        return ProxyBlock.objects.create(proxied_block=proxied_block)

    def edit(self,vals,files):
        proxied_block = PageBlock.objects.get(id=vals.get('proxied_block',''))
        self.proxied_block = proxied_block
        self.save()


    # PageBlock methods that we override to proxy

    def block(self):
        return self.proxied_block.block()

    def render(self,**kwargs):
        return self.proxied_block.render()

    @property
    def js_template_file(self):
        return self.proxied_block.js_template_file

    @property
    def css_template_file(self):
        return self.proxied_block.css_template_file

    def js_render(self,**kwargs):
        return self.proxied_block.render_js()

    def css_render(self,**kwargs):
        return self.proxied_block.render_css()

        

    
