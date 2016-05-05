# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Model Master View
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa
from sqlalchemy import orm

from edbob.util import prettify

import formalchemy
from pyramid import httpexceptions
from pyramid.renderers import get_renderer, render_to_response

from tailbone import forms
from tailbone.views import View
from tailbone.newgrids import filters, AlchemyGrid, GridAction


class MasterView(View):
    """
    Base "master" view class.  All model master views should derive from this.
    """
    filterable = True
    pageable = True
    checkboxes = False

    creatable = True
    viewable = True
    editable = True
    deletable = True

    listing = False
    creating = False
    viewing = False
    editing = False
    deleting = False

    row_attrs = {}
    cell_attrs = {}

    grid_index = None
    use_index_links = False

    @property
    def Session(self):
        """
        SQLAlchemy scoped session to use when querying the database.  Defaults
        to ``tailbone.db.Session``.
        """
        from tailbone.db import Session
        return Session

    ##############################
    # Available Views
    ##############################

    def index(self):
        """
        View to list/filter/sort the model data.

        If this view receives a non-empty 'partial' parameter in the query
        string, then the view will return the renderered grid only.  Otherwise
        returns the full page.
        """
        self.listing = True
        grid = self.make_grid()

        # If user just refreshed the page with a reset instruction, issue a
        # redirect in order to clear out the query string.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            return self.redirect(self.request.current_route_url(_query=None))

        # Stash some grid stats, for possible use when generating URLs.
        if grid.pageable and grid.pager:
            self.first_visible_grid_index = grid.pager.first_item

        # Return grid only, if partial page was requested.
        if self.request.params.get('partial'):
            self.request.response.content_type = b'text/html'
            self.request.response.text = grid.render_grid()
            return self.request.response

        return self.render_to_response('index', {'grid': grid})

    def create(self):
        """
        View for creating a new model record.
        """
        self.creating = True
        form = self.make_form(self.get_model_class())
        if self.request.method == 'POST':
            if form.validate():
                self.save_create_form(form)
                instance = form.fieldset.model
                self.after_create(instance)
                self.request.session.flash("{} has been created: {}".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect_after_create(instance)
        return self.render_to_response('create', {'form': form})

    def save_create_form(self, form):
        self.before_create(form)
        form.save()

    def redirect_after_create(self, instance):
        return self.redirect(self.get_action_url('view', instance))

    def view(self, instance=None):
        """
        View for viewing details of an existing model record.
        """
        self.viewing = True
        if instance is None:
            instance = self.get_instance()
        form = self.make_form(instance)
        return self.render_to_response('view', {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_editable': self.editable_instance(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form})

    def view_index(self):
        """
        View a record according to its grid index.
        """
        try:
            index = int(self.request.GET['index'])
        except KeyError, ValueError:
            return self.redirect(self.get_index_url())
        if index < 1:
            return self.redirect(self.get_index_url())
        data = self.get_effective_data()
        try:
            instance = data[index-1]
        except IndexError:
            return self.redirect(self.get_index_url())
        self.grid_index = index
        if hasattr(data, 'count'):
            self.grid_count = data.count()
        else:
            self.grid_count = len(data)
        return self.view(instance)

    def edit(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        instance = self.get_instance()
        form = self.make_form(instance)

        if self.request.method == 'POST':
            if form.validate():
                self.save_edit_form(form)
                self.request.session.flash("{} has been updated: {}".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect_after_edit(instance)

        return self.render_to_response('edit', {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form})

    def save_edit_form(self, form):
        self.save_form(form)
        self.after_edit(form.fieldset.model)

    def redirect_after_edit(self, instance):
        return self.redirect(self.get_action_url('view', instance))

    def delete(self):
        """
        View for deleting an existing model record.
        """
        if not self.deletable:
            raise httpexceptions.HTTPForbidden()

        self.deleting = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.deletable_instance(instance):
            self.request.session.flash("Deletion is not permitted for {}: {}".format(
                self.get_model_title(), instance_title))
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        # TODO: Add better validation, ideally CSRF etc.
        if self.request.method == 'POST':

            # Let derived classes prep for (or cancel) deletion.
            result = self.before_delete(instance)
            if isinstance(result, httpexceptions.HTTPException):
                return result

            self.delete_instance(instance)
            self.request.session.flash("{} has been deleted: {}".format(
                self.get_model_title(), instance_title))
            return self.redirect(self.get_after_delete_url(instance))

        form.readonly = True
        return self.render_to_response('delete', {
            'instance': instance,
            'instance_title': instance_title,
            'form': form})

    ##############################
    # Core Stuff
    ##############################

    @classmethod
    def get_model_class(cls, error=True):
        """
        Returns the data model class for which the master view exists.
        """
        if not hasattr(cls, 'model_class') and error:
            raise NotImplementedError("You must define the `model_class` for: {}".format(cls))
        return getattr(cls, 'model_class', None)

    @classmethod
    def get_normalized_model_name(cls):
        """
        Returns the "normalized" name for the view's model class.  This will be
        the value of the :attr:`normalized_model_name` attribute if defined;
        otherwise it will be a simple lower-cased version of the associated
        model class name.
        """
        if hasattr(cls, 'normalized_model_name'):
            return cls.normalized_model_name
        return cls.get_model_class().__name__.lower()

    @classmethod
    def get_model_key(cls):
        """
        Return a string name for the primary key of the model class.
        """
        if hasattr(cls, 'model_key'):
            return cls.model_key
        mapper = orm.class_mapper(cls.get_model_class())
        return ','.join([k.key for k in mapper.primary_key])

    @classmethod
    def get_model_title(cls):
        """
        Return a "humanized" version of the model name, for display in templates.
        """
        if hasattr(cls, 'model_title'):
            return cls.model_title
        title = cls.get_model_class().__name__
        # convert "CamelCase" to "Camel Case"
        return re.sub(r'([a-z])([A-Z])', r'\g<1> \g<2>', title)

    @classmethod
    def get_model_title_plural(cls):
        """
        Return a "humanized" (and plural) version of the model name, for
        display in templates.
        """
        return getattr(cls, 'model_title_plural', '{0}s'.format(cls.get_model_title()))

    @classmethod
    def get_route_prefix(cls):
        """
        Returns a prefix which (by default) applies to all routes provided by
        the master view class.  This is the plural, lower-cased name of the
        model class by default, e.g. 'products'.
        """
        model_name = cls.get_normalized_model_name()
        return getattr(cls, 'route_prefix', '{0}s'.format(model_name))

    @classmethod
    def get_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class.  By default this is the route prefix, preceded by a
        slash, e.g. '/products'.
        """
        return getattr(cls, 'url_prefix', '/{0}'.format(cls.get_route_prefix()))

    @classmethod
    def get_template_prefix(cls):
        """
        Returns a prefix which (by default) applies to all templates required by
        the master view class.  This uses the URL prefix by default.
        """
        return getattr(cls, 'template_prefix', cls.get_url_prefix())

    @classmethod
    def get_permission_prefix(cls):
        """
        Returns a prefix which (by default) applies to all permissions leveraged by
        the master view class.  This uses the route prefix by default.
        """
        return getattr(cls, 'permission_prefix', cls.get_route_prefix())

    def get_index_url(self):
        """
        Returns the master view's index URL.
        """
        return self.request.route_url(self.get_route_prefix())

    @classmethod
    def get_index_title(cls):
        """
        Returns the title for the index page.
        """
        return getattr(cls, 'index_title', cls.get_model_title_plural())

    def get_action_url(self, action, instance):
        """
        Generate a URL for the given action on the given instance.
        """
        return self.request.route_url('{0}.{1}'.format(self.get_route_prefix(), action),
                                      **self.get_action_route_kwargs(instance))

    def render_to_response(self, template, data):
        """
        Return a response with the given template rendered with the given data.
        Note that ``template`` must only be a "key" (e.g. 'index' or 'view').
        First an attempt will be made to render using the :attr:`template_prefix`.
        If that doesn't work, another attempt will be made using '/master' as
        the template prefix.
        """
        context = {
            'master': self,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(),
            'action_url': self.get_action_url,
            'grid_index': self.grid_index,
        }
        if self.grid_index:
            context['grid_count'] = self.grid_count
        context.update(data)
        context.update(self.template_kwargs(**context))
        if hasattr(self, 'template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'template_kwargs_{}'.format(template))(**context))

        # First try the template path most specific to the view.
        try:
            return render_to_response('{}/{}.mako'.format(self.get_template_prefix(), template),
                                      context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template):
                try:
                    return render_to_response(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render_to_response('{}/{}.mako'.format(self.get_template_prefix(), template),
                                      context, request=self.request)

    def get_fallback_templates(self, template):
        return ['/master/{}.mako'.format(template)]

    def template_kwargs(self, **kwargs):
        """
        Supplement the template context, for all views.
        """
        return kwargs

    def redirect(self, url):
        """
        Convenience method to return a HTTP 302 response.
        """
        return httpexceptions.HTTPFound(location=url)

    ##############################
    # Grid Stuff
    ##############################

    @classmethod
    def get_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'grid_factory', AlchemyGrid)

    @classmethod
    def get_grid_key(cls):
        """
        Returns the unique key to be used for the grid, for caching sort/filter
        options etc.
        """
        return getattr(cls, 'grid_key', '{0}s'.format(cls.get_normalized_model_name()))

    def make_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new grid instances.
        """
        defaults = {
            'width': 'full',
            'filterable': self.filterable,
            'sortable': True,
            'default_sortkey': getattr(self, 'default_sortkey', None),
            'sortdir': getattr(self, 'sortdir', 'asc'),
            'pageable': self.pageable,
            'checkboxes': self.checkboxes,
            'checked': self.checked,
            'row_attrs': self.get_row_attrs,
            'cell_attrs': self.get_cell_attrs,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'permission_prefix': self.get_permission_prefix(),
            'route_prefix': self.get_route_prefix(),
        }
        if 'main_actions' not in kwargs and 'more_actions' not in kwargs:
            main, more = self.get_grid_actions()
            defaults['main_actions'] = main
            defaults['more_actions'] = more
        defaults.update(kwargs)
        return defaults

    def get_grid_actions(self):
        return self.get_main_actions(), self.get_more_actions()

    def get_row_attrs(self, row, i):
        """
        Returns a dict of HTML attributes which is to be applied to the row's
        ``<tr>`` element.  Note that ``i`` will be a 1-based index value for
        the row within its table.  The meaning of ``row`` is basically not
        defined; it depends on the type of data the grid deals with.
        """
        if callable(self.row_attrs):
            return self.row_attrs(row, i)
        return self.row_attrs

    def get_cell_attrs(self, row, column):
        """
        Returns a dictionary of HTML attributes which should be applied to the
        ``<td>`` element in which the given row and column "intersect".
        """
        if callable(self.cell_attrs):
            return self.cell_attrs(row, column)
        return self.cell_attrs

    def get_main_actions(self):
        """
        Return a list of 'main' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        if self.viewable and self.request.has_perm('{}.view'.format(prefix)):
            url = self.get_view_index_url if self.use_index_links else None
            actions.append(self.make_action('view', icon='zoomin', url=url))
        return actions

    def get_view_index_url(self, row, i):
        route = '{}.view_index'.format(self.get_route_prefix())
        return '{}?index={}'.format(self.request.route_url(route), self.first_visible_grid_index + i - 1)

    def get_more_actions(self):
        """
        Return a list of 'more' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        if self.editable and self.request.has_perm('{}.edit'.format(prefix)):
            actions.append(self.make_action('edit', icon='pencil'))
        if self.deletable and self.request.has_perm('{}.delete'.format(prefix)):
            actions.append(self.make_action('delete', icon='trash', url=self.default_delete_url))
        return actions

    def default_delete_url(self, row, i=None):
        if self.deletable_instance(row):
            return self.request.route_url('{}.delete'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def make_action(self, key, url=None, **kwargs):
        """
        Make a new :class:`GridAction` instance for the current grid.
        """
        if url is None:
            route = '{}.{}'.format(self.get_route_prefix(), key)
            url = lambda r, i: self.request.route_url(route, **self.get_action_route_kwargs(r))
        return GridAction(key, url=url, **kwargs)

    def get_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        try:
            mapper = orm.object_mapper(row)
        except orm.exc.UnmappedInstanceError:
            return {self.model_key: row[self.model_key]}
        else:
            keys = [k.key for k in mapper.primary_key]
            values = [getattr(row, k) for k in keys]
            return dict(zip(keys, values))

    def make_grid(self, **kwargs):
        """
        Make and return a new (configured) grid instance.
        """
        factory = self.get_grid_factory()
        key = self.get_grid_key()
        data = self.get_data(session=kwargs.get('session'))
        kwargs = self.make_grid_kwargs(**kwargs)
        grid = factory(key, self.request, data=data, model_class=self.get_model_class(error=False), **kwargs)
        self._preconfigure_grid(grid)
        self.configure_grid(grid)
        grid.load_settings()
        return grid

    def _preconfigure_grid(self, grid):
        pass

    def configure_grid(self, grid):
        """
        Configure the grid, customizing as necessary.  Subclasses are
        encouraged to override this method.

        As a bare minimum, the logic for this method must at some point invoke
        the ``configure()`` method on the grid instance.  The default
        implementation does exactly (and only) this, passing no arguments.
        This requirement is a result of using FormAlchemy under the hood, and
        it is in fact a call to :meth:`formalchemy:formalchemy.tables.Grid.configure()`.
        """
        if hasattr(grid, 'configure'):
            grid.configure()

    def get_data(self, session=None):
        """
        Generate the base data set for the grid.  This typically will be a
        SQLAlchemy query against the view's model class, but subclasses may
        override this to support arbitrary data sets.

        Note that if your view is typical and uses a SA model, you should not
        override this methid, but override :meth:`query()` instead.
        """
        if session is None:
            session = self.Session()
        return self.query(session)

    def query(self, session):
        """
        Produce the initial/base query for the master grid.  By default this is
        simply a query against the model class, but you may override as
        necessary to apply any sort of pre-filtering etc.  This is useful if
        say, you don't ever want to show records of a certain type to non-admin
        users.  You would modify the base query to hide what you wanted,
        regardless of the user's filter selections.
        """
        return session.query(self.get_model_class())

    def get_effective_data(self, session=None):
        """
        Convenience method which returns the "effective" data for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        if session is None:
            session = self.Session()
        grid = self.make_grid(session=session, pageable=False,
                              main_actions=[], more_actions=[])
        return grid._fa_grid.rows

    def get_effective_query(self, session):
        return self.get_effective_data(session)

    def checkbox(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        rendererd for the given row.  Default implementation returns ``True``
        in all cases.
        """
        return True

    def checked(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        checked by default, for the given row.  Default implementation returns
        ``False`` in all cases.
        """
        return False

    ##############################
    # CRUD Stuff
    ##############################

    def get_instance(self):
        """
        Fetch the current model instance by inspecting the route kwargs and
        doing a database lookup.  If the instance cannot be found, raises 404.
        """
        key = self.request.matchdict[self.get_model_key()]
        instance = self.Session.query(self.get_model_class()).get(key)
        if not instance:
            raise httpexceptions.HTTPNotFound()
        return instance

    def get_instance_title(self, instance):
        """
        Return a "pretty" title for the instance, to be used in the page title etc.
        """
        return unicode(instance)

    def make_form(self, instance, **kwargs):
        """
        Make a FormAlchemy-based form for use with CRUD views.
        """
        # TODO: Some hacky stuff here, to accommodate old form cruft.  Probably
        # should refactor forms soon too, but trying to avoid it for the moment.

        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('editing', self.editing)

        fieldset = self.make_fieldset(instance)
        self._preconfigure_fieldset(fieldset)
        self.configure_fieldset(fieldset)
        self._postconfigure_fieldset(fieldset)

        kwargs.setdefault('action_url', self.request.current_route_url(_query=None))
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url())
        else:
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance))
        factory = kwargs.pop('factory', forms.AlchemyForm)
        form = factory(self.request, fieldset, **kwargs)
        form.readonly = self.viewing
        return form

    def save_form(self, form):
        form.save()

    def make_fieldset(self, instance, **kwargs):
        """
        Make a FormAlchemy fieldset for the given model instance.
        """
        kwargs.setdefault('session', self.Session())
        kwargs.setdefault('request', self.request)
        fieldset = formalchemy.FieldSet(instance, **kwargs)
        fieldset.prettify = prettify
        return fieldset

    def _preconfigure_fieldset(self, fieldset):
        pass

    def configure_fieldset(self, fieldset):
        """
        Configure the given fieldset.
        """
        fieldset.configure()

    def _postconfigure_fieldset(self, fieldset):
        pass

    def before_create(self, form):
        """
        Event hook, called just after the form to create a new instance has
        been validated, but prior to the form itself being saved.
        """

    def after_create(self, instance):
        """
        Event hook, called just after a new instance is saved.
        """

    def editable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def after_edit(self, instance):
        """
        Event hook, called just after an existing instance is saved.
        """

    def deletable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def before_delete(self, instance):
        """
        Event hook, called just before deletion is attempted.
        """

    def delete_instance(self, instance):
        """
        Delete the instance, or mark it as deleted, or whatever you need to do.
        """
        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(instance)
        self.Session.flush()

    def get_after_delete_url(self, instance):
        """
        Returns the URL to which the user should be redirected after
        successfully "deleting" the given instance.
        """
        if hasattr(self, 'after_delete_url'):
            if callable(self.after_delete_url):
                return self.after_delete_url(instance)
            return self.after_delete_url
        return self.get_index_url()

    ##############################
    # Config Stuff
    ##############################

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # list/search
        config.add_route(route_prefix, '{0}/'.format(url_prefix))
        config.add_view(cls, attr='index', route_name=route_prefix,
                        permission='{0}.list'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{0}.list'.format(permission_prefix),
                                       "List/Search {0}".format(model_title_plural))

        # create
        if cls.creatable:
            config.add_route('{0}.create'.format(route_prefix), '{0}/new'.format(url_prefix))
            config.add_view(cls, attr='create', route_name='{0}.create'.format(route_prefix),
                            permission='{0}.create'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.create'.format(permission_prefix),
                                           "Create new {0}".format(model_title))

        # view
        if cls.viewable:
            config.add_tailbone_permission(permission_prefix, '{}.view'.format(permission_prefix),
                                           "View {} details".format(model_title))

            # view by grid index
            config.add_route('{}.view_index'.format(route_prefix), '{}/view'.format(url_prefix))
            config.add_view(cls, attr='view_index', route_name='{}.view_index'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

            # view by record key
            config.add_route('{}.view'.format(route_prefix), '{}/{{{}}}'.format(url_prefix, model_key))
            config.add_view(cls, attr='view', route_name='{}.view'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

        # edit
        if cls.editable:
            config.add_route('{0}.edit'.format(route_prefix), '{0}/{{{1}}}/edit'.format(url_prefix, model_key))
            config.add_view(cls, attr='edit', route_name='{0}.edit'.format(route_prefix),
                            permission='{0}.edit'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.edit'.format(permission_prefix),
                                           "Edit {0}".format(model_title))

        # delete
        if cls.deletable:
            config.add_route('{0}.delete'.format(route_prefix), '{0}/{{{1}}}/delete'.format(url_prefix, model_key))
            config.add_view(cls, attr='delete', route_name='{0}.delete'.format(route_prefix),
                            permission='{0}.delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.delete'.format(permission_prefix),
                                           "Delete {0}".format(model_title))
