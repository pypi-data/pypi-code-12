from django.contrib import admin
from .models import Review
from image_cropping import ImageCroppingMixin

# Register your models here.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	pass