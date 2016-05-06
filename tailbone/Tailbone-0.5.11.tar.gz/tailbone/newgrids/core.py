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
Core Grid Classes
"""

from __future__ import unicode_literals, absolute_import

from edbob.util import prettify

from rattail.db.api import get_setting, save_setting

from pyramid.renderers import render
from webhelpers.html import HTML, tags
from webhelpers.html.builder import format_attrs

from tailbone.db import Session
from tailbone.newgrids import filters


class Grid(object):
    """
    Core grid class.  In sore need of documentation.
    """

    def __init__(self, key, request, columns=[], data=[], main_actions=[], more_actions=[],
                 joiners={}, filterable=False, filters={},
                 sortable=False, sorters={}, default_sortkey=None, default_sortdir='asc',
                 pageable=False, default_pagesize=20, default_page=1,
                 width='auto', checkboxes=False, row_attrs={}, cell_attrs={},
                 **kwargs):
        self.key = key
        self.request = request
        self.columns = columns
        self.data = data
        self.main_actions = main_actions
        self.more_actions = more_actions
        self.joiners = joiners or {} # use new/different empty dict for each instance

        # Set extra attributes first, in case other init logic depends on any
        # of them (i.e. in subclasses).
        for kw, val in kwargs.iteritems():
            setattr(self, kw, val)

        self.filterable = filterable
        if self.filterable:
            self.filters = self.make_filters(filters)

        self.sortable = sortable
        if self.sortable:
            self.sorters = self.make_sorters(sorters)
            self.default_sortkey = default_sortkey
            self.default_sortdir = default_sortdir

        self.pageable = pageable
        if self.pageable:
            self.default_pagesize = default_pagesize
            self.default_page = default_page

        self.width = width
        self.checkboxes = checkboxes
        self.row_attrs = row_attrs or {}
        self.cell_attrs = cell_attrs

    def get_default_filters(self):
        """
        Returns the default set of filters provided by the grid.
        """
        if hasattr(self, 'default_filters'):
            if callable(self.default_filters):
                return self.default_filters()
            return self.default_filters
        return filters.GridFilterSet()

    def make_filters(self, filters=None):
        """
        Returns an initial set of filters which will be available to the grid.
        The grid itself may or may not provide some default filters, and the
        ``filters`` kwarg may contain additions and/or overrides.
        """
        filters, updates = self.get_default_filters(), filters
        if updates:
            filters.update(updates)
        return filters

    def iter_filters(self):
        """
        Iterate over all filters available to the grid.
        """
        return self.filters.itervalues()

    def iter_active_filters(self):
        """
        Iterate over all *active* filters for the grid.  Whether a filter is
        active is determined by current grid settings.
        """
        for filtr in self.iter_filters():
            if filtr.active:
                yield filtr

    def has_active_filters(self):
        """
        Returns boolean indicating whether the grid contains any *active*
        filters, according to current settings.
        """
        for filtr in self.iter_active_filters():
            return True
        return False

    def make_sorters(self, sorters=None):
        """
        Returns an initial set of sorters which will be available to the grid.
        The grid itself may or may not provide some default sorters, and the
        ``sorters`` kwarg may contain additions and/or overrides.
        """
        sorters, updates = {}, sorters
        if updates:
            sorters.update(updates)
        return sorters

    def make_sorter(self, key, foldcase=False):
        """
        Returns a function suitable for a sort map callable, with typical logic
        built in for sorting a data set comprised of dicts, on the given key.
        """
        if foldcase:
            keyfunc = lambda v: v[key].lower()
        else:
            keyfunc = lambda v: v[key]
        return lambda q, d: sorted(q, key=keyfunc, reverse=d == 'desc')

    def load_settings(self, store=True):
        """
        Load current/effective settings for the grid, from the request query
        string and/or session storage.  If ``store`` is true, then once
        settings have been fully read, they are stored in current session for
        next time.  Finally, various instance attributes of the grid and its
        filters are updated in-place to reflect the settings; this is so code
        needn't access the settings dict directly, but the more Pythonic
        instance attributes.
        """
        # Initial settings come from class defaults.
        settings = {}
        if self.sortable:
            settings['sortkey'] = self.default_sortkey
            settings['sortdir'] = self.default_sortdir
        if self.pageable:
            settings['pagesize'] = self.default_pagesize
            settings['page'] = self.default_page
        if self.filterable:
            for filtr in self.iter_filters():
                settings['filter.{0}.active'.format(filtr.key)] = filtr.default_active
                settings['filter.{0}.verb'.format(filtr.key)] = filtr.default_verb
                settings['filter.{0}.value'.format(filtr.key)] = filtr.default_value

        # If user has default settings on file, apply those first.
        if self.user_has_defaults():
            self.apply_user_defaults(settings)

        # If request contains instruction to reset to default filters, then we
        # can skip the rest of the request/session checks.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            pass

        # If request has filter settings, grab those, then grab sort/pager
        # settings from request or session.
        elif self.filterable and self.request_has_settings('filter'):
            self.update_filter_settings(settings, 'request')
            if self.request_has_settings('sort'):
                self.update_sort_settings(settings, 'request')
            else:
                self.update_sort_settings(settings, 'session')
            self.update_page_settings(settings)

        # If request has no filter settings but does have sort settings, grab
        # those, then grab filter settings from session, then grab pager
        # settings from request or session.
        elif self.request_has_settings('sort'):
            self.update_sort_settings(settings, 'request')
            self.update_filter_settings(settings, 'session')
            self.update_page_settings(settings)

        # NOTE: These next two are functionally equivalent, but are kept
        # separate to maintain the narrative...

        # If request has no filter/sort settings but does have pager settings,
        # grab those, then grab filter/sort settings from session.
        elif self.request_has_settings('page'):
            self.update_page_settings(settings)
            self.update_filter_settings(settings, 'session')
            self.update_sort_settings(settings, 'session')

        # If request has no settings, grab all from session.
        elif self.session_has_settings():
            self.update_filter_settings(settings, 'session')
            self.update_sort_settings(settings, 'session')
            self.update_page_settings(settings)

        # If no settings were found in request or session, don't store result.
        else:
            store = False
            
        # Maybe store settings for next time.
        if store:
            self.persist_settings(settings, 'session')

        # If request contained instruction to save current settings as defaults
        # for the current user, then do that.
        if self.request.GET.get('save-current-filters-as-defaults') == 'true':
            self.persist_settings(settings, 'defaults')

        # Update ourself and our filters, to reflect settings.
        if self.filterable:
            for filtr in self.iter_filters():
                filtr.active = settings['filter.{0}.active'.format(filtr.key)]
                filtr.verb = settings['filter.{0}.verb'.format(filtr.key)]
                filtr.value = settings['filter.{0}.value'.format(filtr.key)]
        if self.sortable:
            self.sortkey = settings['sortkey']
            self.sortdir = settings['sortdir']
        if self.pageable:
            self.pagesize = settings['pagesize']
            self.page = settings['page']

    def user_has_defaults(self):
        """
        Check to see if the current user has default settings on file for this grid.
        """
        user = self.request.user
        if not user:
            return False

        session = getattr(self, 'session', Session())
        if user not in session:
            user = session.merge(user)

        # User defaults should have all or nothing, so just check one key.
        key = 'tailbone.{}.grid.{}.sortkey'.format(user.uuid, self.key)
        return get_setting(session, key) is not None

    def apply_user_defaults(self, settings):
        """
        Update the given settings dict with user defaults, if any exist.
        """
        def merge(key, coerce=lambda v: v):
            skey = 'tailbone.{0}.grid.{1}.{2}'.format(self.request.user.uuid, self.key, key)
            value = get_setting(Session(), skey)
            settings[key] = coerce(value)

        if self.filterable:
            for filtr in self.iter_filters():
                merge('filter.{0}.active'.format(filtr.key), lambda v: v == 'true')
                merge('filter.{0}.verb'.format(filtr.key))
                merge('filter.{0}.value'.format(filtr.key))

        if self.sortable:
            merge('sortkey')
            merge('sortdir')

        if self.pageable:
            merge('pagesize', int)
            merge('page', int)

    def request_has_settings(self, type_):
        """
        Determine if the current request (GET query string) contains any
        filter/sort settings for the grid.
        """
        if type_ == 'filter':
            for filtr in self.iter_filters():
                if filtr.key in self.request.GET:
                    return True
            if 'filter' in self.request.GET: # user may be applying empty filters
                return True
        elif type_ == 'sort':
            for key in ['sortkey', 'sortdir']:
                if key in self.request.GET:
                    return True
        elif type_ == 'page':
            for key in ['pagesize', 'page']:
                if key in self.request.GET:
                    return True
        return False

    def session_has_settings(self):
        """
        Determine if the current session contains any settings for the grid.
        """
        # Session should have all or nothing, so just check one key.
        return 'grid.{0}.sortkey'.format(self.key) in self.request.session

    def get_setting(self, source, settings, key, coerce=lambda v: v, default=None):
        """
        Get the effective value for a particular setting, preferring ``source``
        but falling back to existing ``settings`` and finally the ``default``.
        """
        if source not in ('request', 'session'):
            raise ValueError("Invalid source identifier: {0}".format(repr(source)))

        # If source is query string, try that first.
        if source == 'request':
            value = self.request.GET.get(key)
            if value is not None:
                try:
                    value = coerce(value)
                except ValueError:
                    pass
                else:
                    return value

        # Or, if source is session, try that first.
        else:
            value = self.request.session.get('grid.{0}.{1}'.format(self.key, key))
            if value is not None:
                return coerce(value)

        # If source had nothing, try default/existing settings.
        value = settings.get(key)
        if value is not None:
            try:
                value = coerce(value)
            except ValueError:
                pass
            else:
                return value

        # Okay then, default it is.
        return default

    def update_filter_settings(self, settings, source):
        """
        Updates a settings dictionary according to filter settings data found
        in either the GET query string, or session storage.

        :param settings: Dictionary of initial settings, which is to be updated.

        :param source: String identifying the source to consult for settings
           data.  Must be one of: ``('request', 'session')``.
        """
        if not self.filterable:
            return

        for filtr in self.iter_filters():
            prefix = 'filter.{0}'.format(filtr.key)

            if source == 'request':
                # consider filter active if query string contains a value for it
                settings['{0}.active'.format(prefix)] = filtr.key in self.request.GET
                settings['{0}.verb'.format(prefix)] = self.get_setting(
                    source, settings, '{0}.verb'.format(filtr.key), default='')
                settings['{0}.value'.format(prefix)] = self.get_setting(
                    source, settings, filtr.key, default='')

            else: # source = session
                settings['{0}.active'.format(prefix)] = self.get_setting(
                    source, settings, '{0}.active'.format(prefix),
                    coerce=lambda v: unicode(v).lower() == 'true', default=False)
                settings['{0}.verb'.format(prefix)] = self.get_setting(
                    source, settings, '{0}.verb'.format(prefix), default='')
                settings['{0}.value'.format(prefix)] = self.get_setting(
                    source, settings, '{0}.value'.format(prefix), default='')

    def update_sort_settings(self, settings, source):
        """
        Updates a settings dictionary according to sort settings data found in
        either the GET query string, or session storage.

        :param settings: Dictionary of initial settings, which is to be updated.

        :param source: String identifying the source to consult for settings
           data.  Must be one of: ``('request', 'session')``.
        """
        if not self.sortable:
            return
        settings['sortkey'] = self.get_setting(source, settings, 'sortkey')
        settings['sortdir'] = self.get_setting(source, settings, 'sortdir')

    def update_page_settings(self, settings):
        """
        Updates a settings dictionary according to pager settings data found in
        either the GET query string, or session storage.

        Note that due to how the actual pager functions, the effective settings
        will often come from *both* the request and session.  This is so that
        e.g. the page size will remain constant (coming from the session) while
        the user jumps between pages (which only provides the single setting).

        :param settings: Dictionary of initial settings, which is to be updated.
        """
        if not self.pageable:
            return

        pagesize = self.request.GET.get('pagesize')
        if pagesize is not None:
            if pagesize.isdigit():
                settings['pagesize'] = int(pagesize)
        else:
            pagesize = self.request.session.get('grid.{0}.pagesize'.format(self.key))
            if pagesize is not None:
                settings['pagesize'] = pagesize

        page = self.request.GET.get('page')
        if page is not None:
            if page.isdigit():
                settings['page'] = page
        else:
            page = self.request.session.get('grid.{0}.page'.format(self.key))
            if page is not None:
                settings['page'] = page

    def persist_settings(self, settings, to='session'):
        """
        Persist the given settings in some way, as defined by ``func``.
        """
        def persist(key, value=lambda k: settings[k]):
            if to == 'defaults':
                skey = 'tailbone.{0}.grid.{1}.{2}'.format(self.request.user.uuid, self.key, key)
                save_setting(Session(), skey, value(key))
            else: # to == session
                skey = 'grid.{0}.{1}'.format(self.key, key)
                self.request.session[skey] = value(key)

        if self.filterable:
            for filtr in self.iter_filters():
                persist('filter.{0}.active'.format(filtr.key), value=lambda k: unicode(settings[k]).lower())
                persist('filter.{0}.verb'.format(filtr.key))
                persist('filter.{0}.value'.format(filtr.key))

        if self.sortable:
            persist('sortkey')
            persist('sortdir')

        if self.pageable:
            persist('pagesize')
            persist('page')

    def filter_data(self, data):
        """
        Filter and return the given data set, according to current settings.
        """
        for filtr in self.iter_active_filters():
            if filtr.key in self.joiners and filtr.key not in self.joined:
                data = self.joiners[filtr.key](data)
                self.joined.add(filtr.key)
            data = filtr.filter(data)
        return data

    def sort_data(self, data):
        """
        Sort the given query according to current settings, and return the result.
        """
        # Cannot sort unless we know which column to sort by.
        if not self.sortkey:
            return data

        # Cannot sort unless we have a sort function.
        sortfunc = self.sorters.get(self.sortkey)
        if not sortfunc:
            return data

        # We can provide a default sort direction though.
        sortdir = getattr(self, 'sortdir', 'asc')
        if self.sortkey in self.joiners and self.sortkey not in self.joined:
            data = self.joiners[self.sortkey](data)
            self.joined.add(self.sortkey)
        return sortfunc(data, sortdir)

    def paginate_data(self, data):
        """
        Paginate the given data set according to current settings, and return
        the result.  Note that the default implementation does nothing.
        """
        return data

    def make_visible_data(self):
        """
        Apply various settings to the raw data set, to produce a final data
        set.  This will page / sort / filter as necessary, according to the
        grid's defaults and the current request etc.
        """
        self.joined = set()
        data = self.data
        if self.filterable:
            data = self.filter_data(data)
        if self.sortable:
            data = self.sort_data(data)
        if self.pageable:
            self.pager = self.paginate_data(data)
            data = self.pager
        return data

    def render_complete(self, template='/newgrids/complete.mako', **kwargs):
        """
        Render the complete grid, including filters.
        """
        kwargs['grid'] = self
        kwargs.setdefault('allow_save_defaults', True)
        return render(template, kwargs)

    def render_grid(self, template='/newgrids/grid.mako', **kwargs):
        """
        Render the grid to a Unicode string, using the specified template.
        Addition kwargs are passed along as context to the template.
        """
        kwargs['grid'] = self
        kwargs['format_attrs'] = format_attrs
        return render(template, kwargs)

    def render_filters(self, template='/newgrids/filters.mako', **kwargs):
        """
        Render the filters to a Unicode string, using the specified template.
        Additional kwargs are passed along as context to the template.
        """
        # Provide default data to filters form, so renderer can do some of the
        # work for us.
        data = {}
        for filtr in self.iter_active_filters():
            data['{0}.active'.format(filtr.key)] = filtr.active
            data['{0}.verb'.format(filtr.key)] = filtr.verb
            data[filtr.key] = filtr.value

        form = filters.GridFiltersForm(self.request, self.filters, defaults=data)

        kwargs['request'] = self.request
        kwargs['grid'] = self
        kwargs['form'] = filters.GridFiltersFormRenderer(form)
        return render(template, kwargs)

    def get_div_attrs(self):
        """
        Returns a properly-formatted set of attributes which will be applied to
        the parent ``<div>`` element which contains the grid, when the grid is
        rendered.
        """
        classes = ['newgrid']
        if self.width == 'full':
            classes.append('full')
        if self.checkboxes:
            classes.append('selectable')
        return {'class_': ' '.join(classes),
                'data-url': self.request.current_route_url(_query=None),
                'data-permalink': self.request.current_route_url()}

    def iter_visible_columns(self):
        """
        Returns an iterator for all currently-visible columns.
        """
        return iter(self.columns)

    def column_header(self, column):
        """
        Render a header (``<th>`` element) for a grid column.
        """
        kwargs = {'c': column.label}
        if self.sortable and column.key in self.sorters:
            if column.key == self.sortkey:
                kwargs['class_'] = 'sortable sorted {0}'.format(self.sortdir)
            else:
                kwargs['class_'] = 'sortable'
            kwargs['data-sortkey'] = column.key
            kwargs['c'] = tags.link_to(column.label, '#', title=column.title)
        elif column.title:
            kwargs['c'] = HTML.tag('span', title=column.title, c=column.label)
        return HTML.tag('th', **kwargs)

    @property
    def show_actions_column(self):
        """
        Whether or not an "Actions" column should be rendered for the grid.
        """
        return bool(self.main_actions or self.more_actions)

    def render_actions(self, row, i):
        """
        Returns the rendered contents of the 'actions' column for a given row.
        """
        main_actions = filter(None, [self.render_action(a, row, i) for a in self.main_actions])
        more_actions = filter(None, [self.render_action(a, row, i) for a in self.more_actions])
        if more_actions:
            icon = HTML.tag('span', class_='ui-icon ui-icon-carat-1-e')
            link = tags.link_to("More" + icon, '#', class_='more')
            main_actions.append(link + HTML.tag('div', class_='more', c=more_actions))
        return HTML.literal('').join(main_actions)

    def render_action(self, action, row, i):
        """
        Renders an action menu item (link) for the given row.
        """
        url = action.get_url(row, i)
        if url:
            kwargs = {'class_': action.key}
            if action.icon:
                icon = HTML.tag('span', class_='ui-icon ui-icon-{}'.format(action.icon))
                return tags.link_to(icon + action.label, url, **kwargs)
            return tags.link_to(action.label, url, **kwargs)

    def iter_rows(self):
        return self.make_visible_data()

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

    # def get_row_class(self, row, i):
    #     class_ = self.default_row_class(row, i)
    #     if callable(self.extra_row_class):
    #         extra = self.extra_row_class(row, i)
    #         if extra:
    #             class_ = '{0} {1}'.format(class_, extra)
    #     return class_

    def get_row_key(self, row):
        raise NotImplementedError

    def checkbox(self, row):
        return True

    def checked(self, row):
        return False

    def render_checkbox(self, row):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        rendererd for the given row.  Default implementation returns ``True``
        in all cases.
        """
        if not self.checkbox(row):
            return ''
        return tags.checkbox('checkbox-{0}-{1}'.format(self.key, self.get_row_key(row)),
                             checked=self.checked(row))

    def get_cell_attrs(self, row, column):
        """
        Returns a dictionary of HTML attributes which should be applied to the
        ``<td>`` element in which the given row and column "intersect".
        """
        if callable(self.cell_attrs):
            return self.cell_attrs(row, column)
        return self.cell_attrs

    def render_cell(self, row, column):
        return column.render(row[column.key])

    def get_pagesize_options(self):
        # TODO: Make configurable or something...
        return [5, 10, 20, 50, 100]


class GridColumn(object):
    """
    Simple class to represent a column displayed within a grid table.

    .. attribute:: key

       Key for the column, within the context of the grid.

    .. attribute:: label

       Human-facing label for the column, i.e. displayed in the header.
    """

    def __init__(self, key, label=None, title=None):
        self.key = key
        self.label = label or prettify(key)
        self.title = title

    def render(self, value):
        """
        Render the given value, to be displayed within a grid cell.
        """
        return unicode(value)


class GridAction(object):
    """
    Represents an action available to a grid.  This is used to construct the
    'actions' column when rendering the grid.
    """

    def __init__(self, key, label=None, url='#', icon=None):
        self.key = key
        self.label = label or prettify(key)
        self.icon = icon
        self.url = url

    def get_url(self, row, i):
        """
        Returns an action URL for the given row.
        """
        if callable(self.url):
            return self.url(row, i)
        return self.url
