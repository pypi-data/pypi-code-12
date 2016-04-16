from rescuests.models import Request
from django.contrib import admin

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):

  list_filter = ["status"]
  list_display = (
    "uuid",
    "url",
    "current_retries",
    "last_try",
    "comment",
    "status",
    )

  def current_retries(self, instance):
    return "{} / {}".format(instance.retries, instance.max_retries)
