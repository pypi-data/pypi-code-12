from django.contrib.auth.mixins import LoginRequiredMixin

class OwnedObjectQuerysetMixin(LoginRequiredMixin):
    """
    CBV mixin which filters the queryset based on owner.

    Assumes that the model is an OwnedModel, or at least that it has an owner
    foreign key to the auth user.
    """
    def get_queryset(self):
        queryset = super(OwnedObjectQuerysetMixin, self).get_queryset()
        return queryset.filter(owner=self.request.user)


class OwnedObjectFormMixin(LoginRequiredMixin):
    """
    CBV mixin that adds the logged in user's instance to the created object.
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnedObjectFormMixin, self).form_valid(form)
