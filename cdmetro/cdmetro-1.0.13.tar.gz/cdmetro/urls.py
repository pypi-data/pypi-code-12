from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from cdmetro.views import HomeView, VistaModelo, VistaAppsModelo, VistaDetalleApp, VistaEliminarApp, VistaCrearApp, \
    LoginPersonaView, LogOutView, CambiarPassView

urlpatterns = [
    #url(r'^logos/$',EjemploView,name="logos"),

    url(r'^$',login_required(HomeView.as_view(),login_url='/login/'),name="home_metro"),
    url(r'^login/$',LoginPersonaView,name="login_metro"),
    url(r'^logout/$',LogOutView,name="logout_metro"),
    url(r'^password/$',CambiarPassView,name="pass_metro"),
    url(r'^(?P<aplicacion>[^/]+)/$',login_required(VistaModelo,login_url='/login/'),name="vista_modelos_metro"),
    url(r'^(?P<aplicacion>[^/]+)/(?P<modelo>[^/]+)/$',login_required(VistaAppsModelo,login_url='/login/'),name="vista_modelos_apps_metro"),
    url(r'^(?P<aplicacion>[^/]+)/(?P<modelo>[^/]+)/crear/$',login_required(VistaCrearApp,login_url='/login/'),name="vista_crear_modelos_apps_metro"),
    url(r'^(?P<aplicacion>[^/]+)/(?P<modelo>[^/]+)/(?P<id>[^/]+)/$',login_required(VistaDetalleApp,login_url='/login/'),name="vista_detalle_apps_metro"),
    url(r'^(?P<aplicacion>[^/]+)/(?P<modelo>[^/]+)/(?P<id>[^/]+)/eliminar/$',login_required(VistaEliminarApp,login_url='/login/'),name="vista_eliminar_apps_metro"),

]