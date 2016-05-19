import re

from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.cache import cache
from django.shortcuts import (get_object_or_404, redirect, render_to_response,
                              resolve_url)
from django.template import RequestContext
from six import BytesIO, StringIO

from admin_extra_urls.extras import action, ExtraUrlMixin, link

from .models import Choice, Content, Image, RequiredTag, Scene, Story

try:
    from docx import Document
except ImportError:
    Document = None


class ContentInline(admin.TabularInline):
    model = Content
    extra = 0

    def get_formset(self, request, instance, **kwargs):

        class ContentForm(forms.ModelForm):
            class Meta(object):
                model = Content
                exclude = []

        return super(ContentInline, self).get_formset(
            request, instance, form=ContentForm, **kwargs)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    fk_name = "scene"

    readonly_fields = ("admin_link",)

    def admin_link(self, obj):
        return "<a href='{}'>{}</a>".format(
            resolve_url("admin:story_scene_change", obj.next_scene.pk),
            obj.next_scene
        )
    admin_link.short_description = ""
    admin_link.allow_tags = True

    def get_formset(self, request, instance, **kwargs):

        class ChoiceForm(forms.ModelForm):
            class Meta(object):
                model = Choice
                exclude = []
            next_scene = forms.ModelChoiceField(
                label="next",
                queryset=Scene.objects.filter(story=instance.story))

        return super(ChoiceInline, self).get_formset(
            request, instance, form=ChoiceForm, **kwargs)


class SceneAdmin(admin.ModelAdmin):
    inlines = (ContentInline, ChoiceInline)
    search_fields = ("name", )
    list_display = ("name", "story")
    list_filter = ("story", )

    readonly_fields = ("admin_links_to",)

    def admin_links_to(self, obj):
        links = []
        for link in obj.links_to.all():
            print("link", link)
            links.append(
                "<a href='{}'>{}</a>".format(
                    resolve_url("admin:story_scene_change", link.scene.pk),
                    link
                )
            )
        return "<br>".join(links)
    admin_links_to.allow_tags = True
    admin_links_to.short_description = "Links to this scene"


class RequiredTagInline(GenericTabularInline):
    model = RequiredTag
    extra = 0


class ContentAdmin(admin.ModelAdmin):
    search_fields = ("text", )
    inlines = (RequiredTagInline,)


class ChoiceAdmin(admin.ModelAdmin):
    search_fields = ("text", )
    inlines = (RequiredTagInline,)


class StoryImportForm(forms.Form):
    docx_file = forms.FileField()


class SceneInline(admin.TabularInline):
    model = Scene
    extra = 0

    exclude = ("image",)
    readonly_fields = ("link",)

    def link(self, obj):
        return "<a href='../../scene/{}/'>edit</a>".format(obj.id)
    link.allow_tags = True


class StoryAdmin(ExtraUrlMixin, admin.ModelAdmin):
    search_fields = ("name", )
    comparisons = (
        (":", ">="),
        ("=", "="),
        ("==", "="),
        (">", ">"),
        ("<", "<"),
        (">=", ">="),
        ("<=", "<=")
    )

    inlines = [SceneInline]

    def _strip_tags(self, text):

        text = text.strip()

        retval = []
        if text.startswith("["):
            tags, text = text.split("]", 1)
            tags = tags[1:].split(",")
            for tag in tags:
                for operator, compare in self.comparisons:
                    if operator in tag:
                        name, value = tag.split(operator)
                        name = name.strip()
                        value = value.strip()
                        comparison = compare
                        break
                if name not in ("image", "background"):
                    value = int(value)
                retval.append((name, comparison, value))

        return text, retval

    def _get_image(self, story, name):
        print("getting image: {}".format(name))
        try:
            return Image.objects.get(story=story, name=name)
        except Image.DoesNotExist:
            raise Exception("Failed to find image by the name `{}`".format(name))

    @action(label="Import")
    def import_scenes(self, request, pk, *args, **kwargs):
        if not pk:
            messages.success(
                request, "Create the story first, then import scenes")
            return redirect("..")

        instance = get_object_or_404(Story, pk=pk)
        errors = []
        try:
            form = None
            error = None
            cache.set(instance.cache_key, None)
            if request.method == "POST":
                form = StoryImportForm(request.POST, request.FILES)
                scenes = []
                if form.is_valid():
                    filelike = BytesIO(form.cleaned_data["docx_file"].read())
                    doc = Document(filelike)
                    mode = None
                    scene = None
                    content = None
                    choice = None
                    first = True
                    links = []
                    for p in doc.paragraphs:
                        style = p.style.style_id
                        if style == "Heading1":
                            if p.text.strip():
                                instance.name = p.text
                                instance.save()
                                mode = "title"
                        elif style == "Heading2":
                            if p.text.strip():
                                mode = "content"
                                scene = Scene.objects.get_or_create(
                                    story=instance,
                                    name=p.text.strip()
                                )[0]
                                if first:
                                    instance.starting_scene = scene
                                    instance.save()
                                    first = False
                                scenes.append(scene)
                                scene.content_set.all().delete()
                                scene.links_from.all().delete()
                        elif style == "Heading3":
                            # if p.text.strip().lower().startswith("choice"):
                            mode = "choices"
                        elif style == "TextBody" or style == "Normal":
                            if p.text.strip():
                                if p.text.startswith("Your head"):
                                    for run in p.runs:
                                        print(run._r, dir(run._r))
                                if mode == "content":
                                    text = ""
                                    for run in p.runs:
                                        if run.bold:
                                            text += "**{}**".format(run.text)
                                        elif run.italic:
                                            text += "*{}*".format(run.text)
                                        else:
                                            text += run.text
                                    text, tags = self._strip_tags(text)
                                    content = scene.content_set.create(
                                        text=text
                                    )
                                    for name, comparison, value in tags:
                                        if name == "background":
                                            try:
                                                scene.image = self._get_image(
                                                    story=instance,
                                                    name=value
                                                )
                                                scene.save()
                                            except Exception as ex:
                                                errors.append(ex)
                                        elif name == "image":
                                            pass
                                        else:
                                            print("creating tag", name, value, comparison)
                                            content.tags.create(
                                                tag=name,
                                                value=value,
                                                comparison=comparison,
                                            )
                                elif mode == "choices":
                                    try:
                                        text, consequences = p.text.split("=>")
                                        text, tags = self._strip_tags(text)
                                        choice = scene.links_from.create(
                                            text=text
                                        )
                                        for name, value in tags:
                                            choice.tags.create(
                                                tag=name,
                                                value=value,
                                                comparison=comparison,
                                            )
                                        for consequence in consequences.split(","):
                                            consequence = consequence.strip()
                                            if "+" in consequence:
                                                name, value = consequence.split("+", 1)
                                                choice.consequenceattribute_set.create(
                                                    tag=name.strip(),
                                                    value=int(value)
                                                )
                                            elif "-" in consequence:
                                                name, value = consequence.split("-", 1)
                                                choice.consequenceattribute_set.create(
                                                    tag=name.strip(),
                                                    value=-int(value)
                                                )
                                            else:
                                                links.append((choice, consequence))
                                    except Exception as ex:
                                        print("!!! exception:", ex)
                        else:
                            print(p.style.style_id, p.text)
                    for choice, next_scene_name in links:
                        # print("linking choice: {} to scene: {}".format(
                        #     choice, next_scene_name
                        # ))
                        try:
                            if next_scene_name.strip():
                                choice.next_scene = Scene.objects.get(
                                    story=instance,
                                    name__iexact=next_scene_name.strip()
                                )
                                choice.save()
                        except Scene.MultipleObjectsReturned:
                            print("!!! More than one scene named: {}".format(
                                next_scene_name))
                        except Scene.DoesNotExist:
                            print("!!! Can't find next scene named: {}".format(
                                next_scene_name))
                    # TODO: report unused scenes

            else:
                form = StoryImportForm()
        except Exception as ex:
            print(ex)
            import traceback
            traceback.print_exc()
            errors.append(ex)
        response = render_to_response("story/admin_import.html", dict(
            form=form,
            instance=instance,
            errors=errors,
        ), context_instance=RequestContext(request))

        return response


admin.site.register(Story, StoryAdmin)
admin.site.register(Scene, SceneAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Image)
