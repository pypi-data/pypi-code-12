class LareViewMixin(object):
    """
    View mixin that provides lare functionality
    """
    lare_current_namespace = ""  # should be declared at instantiation of View

    def dispatch(self, request, *args, **kwargs):
        request.lare.set_current_namespace(self.lare_current_namespace)
        result = super(LareViewMixin, self).dispatch(request, *args, **kwargs)
        return result


class DefaultLareViewMixin(LareViewMixin):
    lare_site = True
    lare_page = True
    lare_content = True
    lare_inner_content = True

    def dispatch(self, request, *args, **kwargs):
        request.lare.set_current_namespace(self.lare_current_namespace)
        matching_count = request.lare.get_matching_count()
        self.lare_site = matching_count <= 0
        self.lare_page = matching_count <= 1
        self.lare_content = matching_count <= 2
        self.lare_inner_content = matching_count <= 3
        result = super(LareViewMixin, self).dispatch(request, *args, **kwargs)
        return result

    def get_context_data(self, **kwargs):
        context = super(DefaultLareViewMixin, self).get_context_data(**kwargs)
        context.update({'lare_site': self.lare_site,
                        'lare_page': self.lare_page,
                        'lare_content': self.lare_content,
                        'lare_inner_content': self.lare_inner_content})
        return context
