from django.shortcuts import render
from django.views.generic.base import View

# Create your views here.



########################################################################
class Home(View):
    """"""
    template = "app/home.html"

    #----------------------------------------------------------------------
    def get(self, request):
        """"""
        return render(request, self.template)

