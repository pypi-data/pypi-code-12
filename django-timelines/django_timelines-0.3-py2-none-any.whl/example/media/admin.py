from django.contrib import admin
from .models import AudioSet, Audio, PhotoSet, Photo, Video, VideoSet


class AudioSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(AudioSet, AudioSetAdmin)


class AudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Audio, AudioAdmin)


class PhotoSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(PhotoSet, PhotoSetAdmin)


class PhotoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Photo, PhotoAdmin)


class VideoSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(VideoSet, VideoSetAdmin)


class VideoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Video, VideoAdmin)
