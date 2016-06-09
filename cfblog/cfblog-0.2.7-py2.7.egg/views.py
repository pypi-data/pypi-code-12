# coding=utf-8
import json
import traceback

from django.core.cache import cache
from django.http.response import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .conf import settings
from .models import Content
from .response import render, render_content
from .signals import post_publish_signal, pre_publish_signal
from .utils import user_passes_test


def cms_page_index(request):
    return render(request)


@require_POST
@csrf_protect
def save(request, save_type):
    if not request.is_ajax():
        return HttpResponseForbidden()

    if save_type not in ('draft', 'publish'):
        return JsonResponse({'success': False}, status=400)

    if save_type == 'draft':
        test_func = settings.CFBLOG_CAN_EDIT
    else:
        test_func = settings.CFBLOG_CAN_PUBLISH

    return user_passes_test(test_func=test_func)(_save)(request, save_type)


def _save(request, save_type):
    post_data = request.POST

    if any(_ not in post_data for _ in ('auth_data', 'cms_page_id')):
        return JsonResponse({'success': False}, status=400)

    cms_page = get_object_or_404(Content, id=post_data['cms_page_id'])
    draft_date = parse_datetime(post_data['draft_modified'])

    if draft_date and draft_date < cms_page.modified_on:
        return JsonResponse(
            {
                'success': False,
                'draft_error': True,
                'message': 'Draft data was out of date'
            },
            status=200
        )

    try:
        content = json.loads(post_data['auth_data'])
    except:
        return JsonResponse(
            {
                'success': False,
                'message': 'Invalid JSON object'
            },
            status=400
         )
    else:
        cms_page.auth_data.update(content)
        try:
            template_context = cache.get(
                'template_context_{}'.format(cms_page.id)
            )
            render_content(cms_page, request=request,
                           template_context=template_context)
        except Exception as e:
            return JsonResponse(
                {'success': False,
                 'message': 'Unable to parse the new content.\n'
                 'Please check the console for issues.',
                 'exception': unicode(e),
                 'traceback': traceback.format_exc()}
            )
        else:
            if save_type == 'draft':
                cms_page.save()
            else:
                pre_signal_response = pre_publish_signal.send(
                    sender=cms_page._meta.model,
                    cms_page=cms_page
                )
                errors, warns = [], []
                for _, response in pre_signal_response:
                    should_publish, msg = response
                    if should_publish is False:
                        errors.append(msg)
                    elif should_publish is None:
                        warns.append(msg)

                if errors:
                    return JsonResponse(
                        {
                            'success': False,
                            'message_in_detail': '\n'.join(errors),
                            'message': """
                                Unable to publish.
                                Please check console for details
                            """
                        }
                    )
                else:
                    cms_page.publish_cms_content()
                    post_publish_signal.send(
                        sender=cms_page._meta.model,
                        cms_page=cms_page
                    )

                if warns:
                    return JsonResponse(
                        {
                            'success': None,
                            'message_in_details': '\n'.join(warns),
                            'message': """
                                Please check console for warnings
                            """
                        }
                    )

            return JsonResponse({'success': True})
