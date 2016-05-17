#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sendgrid
import random
import string
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from cdmetro.forms import *
from django.db.models import Q
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.conf import settings


def LoginPersonaView(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.add_message(request, messages.WARNING, 'Usuario inactivo')
        else:
            messages.add_message(request, messages.ERROR, u'Usuario y contraseña incorrectos')
    return render_to_response('login_metro.html', context_instance=RequestContext(request))

def id_generator():
        return ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(10))

def CambiarPassView(request):
    username = ''
    if request.POST:
        username = request.POST['username']
        usuario = User.objects.filter(Q(username__contains=username) | Q(email__contains=username)).first()
        #print usuario
        if usuario is not None:
            nuevo_pass=id_generator()
            usuario.set_password(str(nuevo_pass))
            usuario.save()
            message = sendgrid.Mail()
            message.add_to('%s <%s>'%(str(usuario.first_name)+str(usuario.last_name),usuario.email))
            message.set_subject(u'Aviso de reestablecimiento de contraseña')
            message.set_html('Contraseña cambiada su nueva contraseña es: '+str(nuevo_pass))
            message.set_from('%s <%s>' % (settings.NOMBRE,settings.CORREO_SENDGRID))
            message.add_filter('templates', 'template_id', settings.TEMPLATE_SENDGRID)
            status, msg = settings.sg.send(message)
            messages.add_message(request, messages.WARNING, u'Se a enviado la nueva contraseña al correo')
        else:
            messages.add_message(request, messages.ERROR, u'Usuario o correo incorrectos')
    return render_to_response('cambiar_pass_metro.html', context_instance=RequestContext(request))

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect("/")

class HomeView(TemplateView):
    template_name = 'index_metro.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        list_apps=[]
        list_per=[]
        permisos=self.request.user.get_all_permissions()
        app_per=[]
        #print permisos
        for permisos in permisos:
            list_per.append(permisos)
            per= permisos.split('.')
            if per[0] not in app_per:
                app_per.append(per[0])
        #print app_per
        #MENU METRO
        try:
            for app in settings.MENU_METRO:
                # print app['app']+'.view.'+'
                if app['app'] in app_per:
                    list_apps.append(app)
        except:
            for app in settings.INSTALLED_APPS:
                if "apps" in app and not 'metro' in app:
                    app_aux=app.split('.')
                    list_apps.append({'app':app_aux[1],'icon':'icon-chevron-right'})
        context.update({'apps':list_apps})
        context.update({'permisos':list_per})
        #TITULO METRO
        try:
            nombre_app=settings.TITULO_METRO
        except:
            nombre_app='Django Admin'
        context.update({'nombre_app':nombre_app})
        usuario=self.request.user
        context.update({'usuario':usuario})
        context.update({'titulo':settings.TITULO_METRO})

        return context

def VistaModelo(request,aplicacion):
    lista_fields=None
    modelo_buscar=None
    #LISTA DE BOTONES DE LAS APPS DEL MODELO
    lista_apps_botones=[]
    icono=None
    try:
        for app in settings.MENU_METRO:
                if app['app'] == aplicacion:
                    lista_apps_botones=app['models']
                    icono=app['icon']
    except:
        lista_apps_botones=None
    #MENU METRO
    list_apps=[]
    list_per=[]
    permisos=request.user.get_all_permissions()
    app_per=[]
    #print permisos
    for permisos in permisos:
        list_per.append(permisos)
        per= permisos.split('.')
        if per[0] not in app_per:
            app_per.append(per[0])
    #print app_per
    #MENU METRO
    try:
        for app in settings.MENU_METRO:
            # print app['app']+'.view.'+'
            if app['app'] in app_per:
                list_apps.append(app)
    except:
        for app in settings.INSTALLED_APPS:
            if "apps" in app and not 'metro' in app:
                app_aux=app.split('.')
                list_apps.append({'app':app_aux[1],'icon':'icon-chevron-right'})
    #TITULO METRO
    titulo=aplicacion
    try:
        nombre_app=settings.TITULO_METRO
    except:
        nombre_app='Django Admin'
    usuario=request.user
    return render_to_response('vista_modelos.html', {
        'apps':list_apps,'lista_apps_botones':lista_apps_botones,
         'titulo':titulo,'usuario':usuario,
         'nombre_app':nombre_app,'icono':icono,
         'permisos':list_per},context_instance=RequestContext(request))


def VistaAppsModelo(request,aplicacion,modelo):
    list_apps=[]
    lista_fields=None
    #MENU METRO
    list_per=[]
    permisos=request.user.get_all_permissions()
    app_per=[]
    #print permisos
    for permisos in permisos:
        list_per.append(permisos)
        per= permisos.split('.')
        if per[0] not in app_per:
            app_per.append(per[0])
    #print app_per
    #MENU METRO
    try:
        for app in settings.MENU_METRO:
            # print app['app']+'.view.'+'
            if app['app'] in app_per:
                list_apps.append(app)
                #print list_apps
    except:
        for app in settings.INSTALLED_APPS:
            if "apps" in app and not 'metro' in app:
                app_aux=app.split('.')
                list_apps.append({'app':app_aux[1],'icon':'icon-chevron-right'})
    try:
        nombre_app=settings.TITULO_METRO
    except:
        nombre_app='Django Admin'
    usuario=request.user
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    nom_modelo= mymodel._meta.verbose_name.title()
    #TITULO METRO
    titulo=nom_modelo
    #print mymodel
    try:
        nombre_app=settings.TITULO_METRO
    except:
        nombre_app='Django Admin'
    #campos
    try:
        lista=mymodel.CamposMetro(request)
        lista_fields=lista[0]['lista']
        titulo_field=lista[0]['titulo']
    except:
        lista_fields=['id',]
        titulo_field=['id',]
    if not lista_fields:
        lista_fields=['id',]
        titulo_field=['id',]
    try:
        lista_buscar=mymodel.FiltroBuscar(request)
    except:
        lista_buscar=mymodel.objects.all()
    url=request.get_full_path()
    return render_to_response('vista_modelos_apps.html',{'apps':list_apps,
        'titulo':titulo,'usuario':usuario,'nombre_app':nombre_app,
        'lista_fields':lista_fields,'titulo_field':titulo_field,'lista_buscar':lista_buscar,
        'modelo':modelo,'nom_modelo':nom_modelo,'aplicacion':aplicacion,
        'permisos':list_per,'url':url},context_instance=RequestContext(request))

def VistaDetalleApp(request,aplicacion,modelo,id):
    list_apps=[]
    lista_fields=None
    modelo_buscar=None
    #MENU METRO
    list_per=[]
    permisos=request.user.get_all_permissions()
    app_per=[]
    #print permisos
    for permisos in permisos:
        list_per.append(permisos)
        per= permisos.split('.')
        if per[0] not in app_per:
            app_per.append(per[0])
    try:
        for app in settings.MENU_METRO:
            # print app['app']+'.view.'+'
            if app['app'] in app_per:
                list_apps.append(app)
    except:
        for apps in settings.INSTALLED_APPS:
            if "apps" in apps and not 'metro' in apps:
                app_aux=apps.split('.')
                list_apps.append({'app':app_aux[1],'icon':'icon-chevron-right'})

    #print list_per
    if not aplicacion+'.change_'+modelo in list_per:
        raise Http404
    usuario=request.user
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    nom_modelo= mymodel._meta.verbose_name.title()
    #TITULO METRO
    titulo=nom_modelo
    #print mymodel
    if not mymodel:
        raise Http404
    try:
        nombre_app=settings.TITULO_METRO
    except:
        nombre_app='Django Admin'
    objeto=get_object_or_404(mymodel, pk=id)
    try:
        inlines=mymodel.InlinesMetro(request,objeto)
    except:
        inlines=None
    #validar formulario
    
    #print objeto
    form =GetForm(request,aplicacion,modelo,objeto)
    if request.method == 'POST':
        form = GetFormRequest(request,aplicacion,modelo,objeto)
        if not inlines:
            if form.is_valid():
                form_save = form.save(commit=False)
                #print form_save.cleaned_data['logo']
                form_save.save()
                #print request.get_full_path()
                return redirect(request.get_full_path(),permanent=True)
        else:
            if form.is_valid():
                form_save = form.save(commit=False)
                #print form_save.cleaned_data['logo']
                form_save.save()
                #print request.get_full_path()
            for a in inlines:
                form_aux=a['formulario'](request.POST,request.FILES)
                if form_aux.is_valid():
                    form_save_aux = form_aux.save(commit=False)
                    form_save_aux.save()
                    return redirect(request.get_full_path(),permanent=True)
    try:
        lista_buscar=mymodel.FiltroBuscar(request)
    except:
        lista_buscar=mymodel.objects.all()
    try:
        acciones=mymodel.AccionesMetro(request)
    except:
        acciones=None
    url=request.get_full_path()
    return render_to_response('vista_detalle_apps.html', {
        'apps':list_apps,'titulo':titulo,'usuario':usuario,'url':url,
        'nombre_app':nombre_app,'modelo':modelo,'nom_modelo':nom_modelo,
        'aplicacion':aplicacion,'lista_buscar':lista_buscar,
        'lista_fields':lista_fields,'objeto':objeto,'permisos':list_per,
        'inlines':inlines,'form':form,'acciones':acciones},
        context_instance=RequestContext(request))

def VistaCrearApp(request,aplicacion,modelo):
    list_apps=[]
    modelo_buscar=None
    #MENU METRO
    list_per=[]
    permisos=request.user.get_all_permissions()
    app_per=[]
    #print permisos
    for permisos in permisos:
        list_per.append(permisos)
        per= permisos.split('.')
        if per[0] not in app_per:
            app_per.append(per[0])
    try:
        for app in settings.MENU_METRO:
            # print app['app']+'.view.'+'
            if app['app'] in app_per:
                list_apps.append(app)
    except:
        for apps in settings.INSTALLED_APPS:
            if "apps" in apps and not 'metro' in apps:
                app_aux=apps.split('.')
                list_apps.append({'app':app_aux[1],'icon':'icon-chevron-right'})
    try:
        nombre_app=settings.TITULO_METRO
    except:
        nombre_app='Django Admin'
    if not aplicacion+'.add_'+modelo in list_per:
        raise Http404
    usuario=request.user
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    nom_modelo= mymodel._meta.verbose_name.title()
    #TITULO METRO
    titulo=nom_modelo
    #print mymodel
    if not mymodel:
        raise Http404
    try:
        lista=mymodel.CamposMetro(request)
        lista_fields=lista[0]['lista']
        titulo_field=lista[0]['titulo']
    except:
        lista_fields=['id',]
        titulo_field=['id',]
    if not lista_fields:
        lista_fields=['id',]
        titulo_field=['id',]
    #validar formulario
    
    if request.method == 'POST':
        form = GetFormRequest(request,aplicacion,modelo,None)
        #print nombre_modelo
        if form.is_valid():
            form_save = form.save(commit=False)
            form_save.save()
            url=request.get_full_path().split('/')
            return redirect('/'+url[1]+'/'+url[2]+'/')
    else:
        form =GetForm(request,aplicacion,modelo,None)
    lista_buscar=mymodel.objects.all()
    
    return render_to_response('vista_crear_modelo.html', 
        {'apps':list_apps,'titulo':titulo,'usuario':usuario,
        'nombre_app':nombre_app,'modelo':modelo,'nom_modelo':nom_modelo,
        'aplicacion':aplicacion,'lista_buscar':lista_buscar,
        'lista_fields':lista_fields,'titulo_field':titulo_field,
        'permisos':list_per,'form':form},
        context_instance=RequestContext(request))

def VistaEliminarApp(request,aplicacion,modelo,id):
    permisos=request.user.get_all_permissions()
    if not aplicacion+'.delete_'+modelo in permisos:
        return HttpResponse('No Tienes Permiso')
    modelo_buscar=get_model(aplicacion,modelo)
    objeto_borrar=modelo_buscar.objects.filter(id=id).first()
    if objeto_borrar:
        try:
            modelo_buscar.Borrar(objeto_borrar)
            return HttpResponse('Eliminado Correctamente')
        except:
            objeto_borrar.delete()
            return HttpResponse('Eliminado Correctamente')
    else:
        return HttpResponse('No Encontrado')



