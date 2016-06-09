from django.conf import settings

urlpatterns = []

for feature in settings.APP.features:
    feature.configure_urls(urlpatterns)

