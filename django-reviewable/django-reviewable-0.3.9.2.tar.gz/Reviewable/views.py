from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, Http404
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView
from .models import Review, Reviewable


class BaseReviewableViewMixin(object):
    """Provides basic methods tht all reviewable views use.

    Provides the review object and adds it to the template context using actual object type as the name.
    Provides a method to override templates for each reviewable model. Simply create a template in the reviewable apps
    template directory that follows: "<model_name>_review_[create/list/detail/confirm_delete/update].html
    """

    def render_to_response(self, context, **kwargs):
        """Check the object is reviewable"""
        if not isinstance(self.review_object, Reviewable):
            raise Http404
        return super(BaseReviewableViewMixin, self).render_to_response(context, **kwargs)

    @property
    def review_object(self):
        """Returns the model object that is being reviewed"""
        raise TypeError('%s must implement the review_object property' % self.__class__.__name__)

    model = Review

    @property
    def label(self):
        return self.review_object._meta.app_label

    def get_context_data(self, **kwargs):
        context = super(BaseReviewableViewMixin, self).get_context_data(**kwargs)
        context[self.label.lower()] = self.review_object # add the reviewable object to the context
        return context

    def get_template_names(self):
        # Search for templates in reviewable object directory
        if not self.template_name:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")

        templates = []
        custom_template = self.label + '/' + self.label.lower() + '_' + self.template_name
        templates.append(custom_template)
        templates.append('Reviewable/' + self.template_name)
        return templates


class ReviewableViewMixin(BaseReviewableViewMixin):
    """Mixin for the update, detail and delete views"""
    @property
    def review_object(self):
        return self.object.review_object


class ReviewableCreateListViewMixin(BaseReviewableViewMixin):
    """Mixin for the create and list views"""
    @property
    def review_object(self):
        """Returns the model object that is being reviewed"""
        try:
            model = ContentType.objects.get(model=
                self.kwargs.get('content_type')
            )
        except ContentType.DoesNotExist:
            raise Http404

        model_class = model.model_class()
        review_object_id=self.kwargs['pk']
        return model_class.objects.get(pk=review_object_id)


class ReviewCreate(LoginRequiredMixin, ReviewableCreateListViewMixin, CreateView):
    """View to create a review for the given object

    This gets the reviewable object based upon the URL arguments.
    Also adds the reviewable_object to the context for easy use.
    """
    template_name = 'review_create.html'
    fields = ['title', 'review', 'rating']

    def get_success_url(self):
        return reverse('Reviewable:review-detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """Save the review using the Reviewable instance

        Redirects to the Review models get_absolute_url
        """
        review = self.review_object.review(self.request.user, form.cleaned_data['title'], form.cleaned_data['review'], form.cleaned_data['rating'])
        self.object = review # Assign the created review as the object
        return HttpResponseRedirect(self.get_success_url())


class ReviewDelete(LoginRequiredMixin, ReviewableViewMixin, DeleteView):
    success_url = getattr(settings, 'REVIEW_DELETE_SUCCESS_URL', '/')
    template_name = 'review_confirm_delete.html'


class ReviewUpdate(LoginRequiredMixin, ReviewableViewMixin, UpdateView):
    template_name = 'review_update.html'
    fields = ['title', 'review', 'rating']


class ReviewDetail(ReviewableViewMixin, DetailView):
    template_name = 'review_detail.html'


class ReviewList(ReviewableCreateListViewMixin, ListView):
    """Extensible view to list all the reviews for a model object"""
    template_name = 'review_list.html'
    context_object_name = 'review_list'

    def get_queryset(self):
        return self.review_object.reviews.all()
