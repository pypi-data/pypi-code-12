from django.conf import settings
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView

from api import ButterCms

BLOG_DIRECTORY = 'blog/'
BLOG_BASE_TEMPLATE = '%sblog_base.html' % BLOG_DIRECTORY
BLOG_POST_TEMPLATE = '%sblog_post.html' % BLOG_DIRECTORY
BLOG_AUTHOR_TEMPLATE = '%sblog_author.html' % BLOG_DIRECTORY
BLOG_CATEGORY_TEMPLATE = '%sblog_category.html' % BLOG_DIRECTORY


class BlogHome(TemplateView):

    def get_template_names(self):
        return [BLOG_BASE_TEMPLATE]

    def get_context_data(self, **kwargs):
        context = super(BlogHome, self).get_context_data(**kwargs)

        # Check if page was passed via url match.
        try:
            page = kwargs['page']
        except:
            page = None

        butter = ButterCms()
        response = butter.get_posts(page)
        context['next_page'] = response['next_page']
        context['previous_page'] = response['previous_page']
        context['recent_posts'] = response['results']
        return context


class BlogPost(TemplateView):

    def get_template_names(self):
        return [BLOG_POST_TEMPLATE]

    def get_context_data(self, **kwargs):
        context = super(BlogPost, self).get_context_data(**kwargs)

        butter = ButterCms()
        context['post'] = butter.get_post(kwargs['slug'])
        context['post']['body'] = mark_safe(context['post']['body'])
        return context


class AuthorPage(TemplateView):

    def get_template_names(self):
        return [BLOG_AUTHOR_TEMPLATE]

    def get_context_data(self, **kwargs):
        context = super(AuthorPage, self).get_context_data(**kwargs)

        butter = ButterCms()
        response = butter.get_author(kwargs['author_slug'])
        context['first_name'] = response['first_name']
        context['last_name'] = response['last_name']
        context['email'] = response['email']
        context['recent_posts'] = response['recent_posts']
        return context


class CategoryPage(TemplateView):

    def get_template_names(self):
        return [BLOG_CATEGORY_TEMPLATE]

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)

        butter = ButterCms()
        response = butter.get_category(kwargs['category_slug'])
        context['category_name'] = response['name']
        context['recent_posts'] = response['recent_posts']
        return context