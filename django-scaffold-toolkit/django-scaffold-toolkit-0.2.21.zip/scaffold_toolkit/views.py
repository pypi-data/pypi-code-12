# coding=utf-8
import json
import datetime
from braces.views import AjaxResponseMixin, JSONResponseMixin, PermissionRequiredMixin, LoginRequiredMixin
from django.core.files.storage import default_storage
from django.shortcuts import resolve_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, FormView
from scaffold_toolkit.utilities.misc import get_form_error_message
import shortuuid
from braces.views import OrderableListMixin as olm
from tagging.models import Tag


class AjaxFormView(JSONResponseMixin, AjaxResponseMixin, FormView):
    content_type = u"application/json; charset=UTF-8"

    def form_invalid(self, form):
        """
        表单校验错误
        :param form:
         :type form: django.forms.form
        :return:
        """
        return self.render_json_response({'success': False,
                                          'msg': get_form_error_message(form)})


class AjaxView(JSONResponseMixin, AjaxResponseMixin, View):
    content_type = u"application/json; charset=UTF-8"


class PermissionRequiredAjaxView(PermissionRequiredMixin, AjaxView):
    """
    有权限要求的AjaxView
    """

    def no_permissions_fail(self, request=None):
        return self.render_json_response({'success': False, 'msg': u'没有权限'})


class LoginRequiredAjaxView(LoginRequiredMixin, AjaxView):
    """
    有登录要求的AjaxView
    """

    def no_permissions_fail(self, request=None):
        return self.render_json_response({'success': False, 'msg': u'请先登录'})


class DialogMixin(object):
    def get_success_url(self):
        return resolve_url('dialog_success')


class NextRedirectMixin(object):
    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)


class OrderableListMixin(olm):
    """
    根据zui.datatable排序
    """

    def get_ordered_queryset(self, queryset=None):
        """
        Augments ``QuerySet`` with order_by statement if possible

        :param QuerySet queryset: ``QuerySet`` to ``order_by``
        :return: QuerySet
        """
        if 'order_by' in self.request.GET:
            return super(OrderableListMixin, self).get_ordered_queryset(queryset)
        try:
            get_order_by = int(self.request.GET.get("index"))

            order_by = self.get_orderable_columns()[get_order_by]
            if not order_by:
                order_by = self.get_orderable_columns_default()
        except:
            order_by = self.get_orderable_columns_default()

        self.order_by = order_by
        self.ordering = 'desc' if order_by.startswith("-") else "asc"

        if order_by and self.request.GET.get("ordering", "asc") == "desc":
            order_by = "-" + order_by if not order_by.startswith("-") else order_by
            self.ordering = "desc"

        return queryset.order_by(order_by)


IMAGE_EXT_NAMES = getattr(settings, 'KINDEDITOR_IMAGE_EXT', ('.jpg', '.png', '.gif', '.bmp'))
FLASH_EXT_NAMES = getattr(settings, 'KINDEDITOR_FLASH_EXT', ('.swf'))
MAX_SIZE = getattr(settings, 'KINDEDITOR_UPLOAD_SIZE', 5) * 1024 * 1024  # 5M
MAX_SIZE_M = MAX_SIZE / 1024 / 1024

storage = default_storage


@csrf_exempt
@require_http_methods(['POST'])
def kindeditor_upload_file(request):
    uploaded_file = request.FILES['imgFile']

    if not uploaded_file.name:
        return HttpResponse(json.dumps({'error': 1, 'message': u'请选择要上传的文件'}))

    ext = os.path.splitext(uploaded_file.name)[1]
    upload_dir = request.GET['dir']
    allowed_exts = None
    if upload_dir == 'image':
        allowed_exts = IMAGE_EXT_NAMES
    elif upload_dir == 'flash':
        allowed_exts = FLASH_EXT_NAMES
    elif upload_dir == 'media':
        pass
    if allowed_exts is not None and ext not in allowed_exts:
        return HttpResponse(json.dumps({'error': 1, 'message': u'不允许的文件格式'}))

    if uploaded_file.size > MAX_SIZE:
        return HttpResponse(json.dumps(
            {'error': 1, 'message': u'上传的文件大小不能超过%sMB' % MAX_SIZE_M}
        ))

    upload_to = os.path.join(datetime.date.today().strftime('kindeditor/upload%Y'),
                             datetime.date.today().strftime("%m%d"))

    file_name = shortuuid.uuid() + ext

    final_name = storage.save(os.path.join(upload_to, file_name), uploaded_file)

    url_name = storage.url(final_name)
    return HttpResponse(json.dumps(
        {'error': 0, 'url': url_name}
    ))


MAX_RESULT = getattr(settings, 'MAX_RESULT', 10)


def tag_suggestion(request):
    """
    tag建议
    @param request:
    @return:
    """
    term = request.GET.get('term')

    tags = [{'id': tag.name, 'text': tag.name}
            for tag in Tag.objects.filter(name__icontains=term)[:MAX_RESULT]]
    return JsonResponse(tags, safe=False)
