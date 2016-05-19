import base64
import json

import markdown
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import mark_safe


@python_2_unicode_compatible
class Image(models.Model):
    story = models.ForeignKey("Story")
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to="content/%Y/%m/", blank=True, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Story(models.Model):
    name = models.CharField(max_length=255)
    starting_scene = models.ForeignKey(
        "Scene", null=True, blank=True, related_name="starting")

    class Meta:
        verbose_name_plural = "Stories"

    def __str__(self):
        return self.name

    @property
    def cache_key(self):
        return "story-2-{}".format(self.id)

    def to_json(self):
        dataset = cache.get(self.cache_key)

        # TODO: cache this better
        if True or not dataset:
            dataset = dict(
                meta=dict(
                    name=self.name,
                    start=self.starting_scene_id,
                )
            )
            scenes = []
            for scene in self.scene_set.all():
                scenes.append(scene.to_dict())
            dataset['scenes'] = scenes

            cache.set(self.cache_key, dataset, 60 * 60 * 4)
        return json.dumps(dataset)


@python_2_unicode_compatible
class Scene(models.Model):
    story = models.ForeignKey(Story)
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ForeignKey(
        Image, verbose_name="Background Image", null=True, blank=True)

    def __str__(self):
        return "{name}".format(
            story=self.story,
            name=self.name or "#{}".format(self.id))

    def to_dict(self):
        return dict(
            meta=dict(
                id=self.id,
                name=self.name
            ),
            image=self.image and self.image.image.url or None,
            content=[c.to_dict() for c in self.content_set.all()],
            choices=[c.to_dict() for c in self.links_from.all()],
        )


@python_2_unicode_compatible
class RequiredTag(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()

    tag = models.CharField(max_length=50)
    comparison = models.CharField(max_length=10, choices=(
        (">", ">"),
        ("<", "<"),
        ("=", "=")
    ), default=">=")
    value = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.tag


@python_2_unicode_compatible
class Content(models.Model):
    scene = models.ForeignKey(Scene)
    ordering = models.SmallIntegerField(default=0)

    # grouping content will make only one show, whichever has the highest
    # ordering and matches the character tags
    group = models.CharField(max_length=50, default="default")
    tags = GenericRelation(RequiredTag)
    text = models.TextField()
    audio = models.FileField(upload_to="content/%Y/%m/", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Content"
        ordering = ("ordering",)

    def __str__(self):
        return u"{}: {}".format(self.scene, self.text[:25] + u"...")

    @property
    def formatted_text(self):
        return mark_safe(markdown.markdown(self.text))

    @property
    def image_data_url(self):
        if self.image:
            return "data:image/png;base64,{}".format(
                base64.b64encode(self.image.image.read())
            )
        return None

    def to_dict(self):
        return dict(
            text=self.formatted_text,
            audio=self.audio and self.audio.url or None,
            tags=list(self.tags.values("tag", "comparison", "value"))
        )


@python_2_unicode_compatible
class Choice(models.Model):
    scene = models.ForeignKey(Scene, related_name="links_from")
    text = models.CharField(max_length=255)
    next_scene = models.ForeignKey(
        Scene, related_name="links_to", blank=True, null=True)
    tags = GenericRelation(RequiredTag)

    def __str__(self):
        return u"{}: {}".format(self.scene, self.text[:25] + u"...")

    @property
    def formatted_text(self):
        return mark_safe(markdown.markdown(self.text))[3:-4]

    def to_dict(self):
        return dict(
            text=self.formatted_text,
            next_scene=self.next_scene_id,
            tags=list(self.tags.values("tag", "comparison", "value")),
            consequences=list(self.consequenceattribute_set.values(
                "tag", "value"
            ))
        )

    # def link(self):
    #     if self.next_scene:
    #         return resolve_url


# @python_2_unicode_compatible
class Consequence(models.Model):
    choice = models.ForeignKey(Choice)
    module = models.CharField(max_length=255)


# @python_2_unicode_compatible
class ConsequenceAttribute(models.Model):
    choice = models.ForeignKey(Choice)
    tag = models.CharField(max_length=50)
    value = models.SmallIntegerField(default=1)
