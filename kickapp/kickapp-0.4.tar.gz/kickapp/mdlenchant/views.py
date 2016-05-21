from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse
# Create your views here.


from webbrowser import open_new_tab


########################################################################
class OpenLink(View):
    #----------------------------------------------------------------------
    def get(self, request):
        """"""

        url = request.GET.get("url", False)
        if url:
            open_new_tab(url)

        return JsonResponse({"success": bool(url),})
