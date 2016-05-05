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
Product Views
"""

from __future__ import unicode_literals, absolute_import

import os
import re

import sqlalchemy as sa
from sqlalchemy import orm

from rattail import enum, pod, sil, batches
from rattail.db import model, api, auth, Session as RattailSession
from rattail.gpc import GPC
from rattail.threads import Thread
from rattail.exceptions import LabelPrintingError

import formalchemy as fa
from pyramid import httpexceptions
from pyramid.renderers import render_to_response
from webhelpers.html import tags

from tailbone import forms, newgrids as grids
from tailbone.db import Session
from tailbone.views import MasterView, SearchableAlchemyGridView, AutocompleteView
from tailbone.views.continuum import VersionView, version_defaults
from tailbone.forms.renderers import products as products_forms
from tailbone.progress import SessionProgress


# TODO: For a moment I thought this was going to be necessary, but now I think
# not.  Leaving it around for a bit just in case...

# class VendorAnyFilter(grids.filters.AlchemyStringFilter):
#     """
#     Custom filter for "vendor (any)" so we can avoid joining on that unless we
#     really have to.  This is because it seems to throw off the number of
#     records which are showed in the result set, when this filter is included in
#     the active set but no criteria is specified.
#     """

#     def filter(self, query, **kwargs):
#         original = query
#         query = super(VendorAnyFilter, self).filter(query, **kwargs)
#         if query is not original:
#             query = self.joiner(query)
#         return query


class DescriptionFieldRenderer(fa.TextFieldRenderer):
    """
    Renderer for product descriptions within the grid; adds hyperlink.
    """

    def render_readonly(self, **kwargs):
        description = self.raw_value
        if description is None:
            return ''
        if kwargs.get('link'):
            product = self.field.parent.model
            description = tags.link_to(description, kwargs['link'](product))
        return description


class ProductsView(MasterView):
    """
    Master view for the Product class.
    """
    model_class = model.Product

    # child_version_classes = [
    #     (model.ProductCode, 'product_uuid'),
    #     (model.ProductCost, 'product_uuid'),
    #     (model.ProductPrice, 'product_uuid'),
    #     ]

    # These aliases enable the grid queries to filter products which may be
    # purchased from *any* vendor, and yet sort by only the "preferred" vendor
    # (since that's what shows up in the grid column).
    ProductCostAny = orm.aliased(model.ProductCost)
    VendorAny = orm.aliased(model.Vendor)

    def __init__(self, request):
        self.request = request
        self.print_labels = request.rattail_config.getbool('tailbone', 'products.print_labels', default=False)

    def query(self, session):
        user = self.request.user
        if user and user not in session:
            user = session.merge(user)

        query = session.query(model.Product)
        if not auth.has_permission(session, user, 'products.view_deleted'):
            query = query.filter(model.Product.deleted == False)

        # TODO: This used to be a good idea I thought...but in dev it didn't
        # seem to make much difference, except with a larger (50K) data set it
        # totally bogged things down instead of helping...
        # query = query\
        #     .options(orm.joinedload(model.Product.brand))\
        #     .options(orm.joinedload(model.Product.department))\
        #     .options(orm.joinedload(model.Product.subdepartment))\
        #     .options(orm.joinedload(model.Product.regular_price))\
        #     .options(orm.joinedload(model.Product.current_price))\
        #     .options(orm.joinedload(model.Product.vendor))

        return query

    def configure_grid(self, g):

        def join_vendor(q):
            return q.outerjoin(model.ProductCost,
                               sa.and_(
                                   model.ProductCost.product_uuid == model.Product.uuid,
                                   model.ProductCost.preference == 1))\
                    .outerjoin(model.Vendor)

        def join_vendor_any(q):
            return q.outerjoin(self.ProductCostAny,
                               self.ProductCostAny.product_uuid == model.Product.uuid)\
                    .outerjoin(self.VendorAny,
                               self.VendorAny.uuid == self.ProductCostAny.vendor_uuid)

        g.joiners['brand'] = lambda q: q.outerjoin(model.Brand)
        g.joiners['family'] = lambda q: q.outerjoin(model.Family)
        g.joiners['department'] = lambda q: q.outerjoin(model.Department,
                                                        model.Department.uuid == model.Product.department_uuid)
        g.joiners['subdepartment'] = lambda q: q.outerjoin(model.Subdepartment,
                                                           model.Subdepartment.uuid == model.Product.subdepartment_uuid)
        g.joiners['report_code'] = lambda q: q.outerjoin(model.ReportCode)
        g.joiners['regular_price'] = lambda q: q.outerjoin(model.ProductPrice,
                                                           model.ProductPrice.uuid == model.Product.regular_price_uuid)
        g.joiners['current_price'] = lambda q: q.outerjoin(model.ProductPrice,
                                                           model.ProductPrice.uuid == model.Product.current_price_uuid)
        g.joiners['code'] = lambda q: q.outerjoin(model.ProductCode)
        g.joiners['vendor'] = join_vendor
        g.joiners['vendor_any'] = join_vendor_any

        g.sorters['brand'] = g.make_sorter(model.Brand.name)
        g.sorters['department'] = g.make_sorter(model.Department.name)
        g.sorters['subdepartment'] = g.make_sorter(model.Subdepartment.name)
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.filters['upc'].default_active = True
        g.filters['upc'].default_verb = 'equal'
        g.filters['upc'].label = "UPC"
        g.filters['description'].default_active = True
        g.filters['description'].default_verb = 'contains'
        g.filters['brand'] = g.make_filter('brand', model.Brand.name,
                                           default_active=True, default_verb='contains')
        g.filters['family'] = g.make_filter('family', model.Family.name)
        g.filters['department'] = g.make_filter('department', model.Department.name,
                                                default_active=True, default_verb='contains')
        g.filters['subdepartment'] = g.make_filter('subdepartment', model.Subdepartment.name)
        g.filters['report_code'] = g.make_filter('report_code', model.ReportCode.name)
        g.filters['code'] = g.make_filter('code', model.ProductCode.code)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name, label="Vendor (preferred)")
        g.filters['vendor_any'] = g.make_filter('vendor_any', self.VendorAny.name, label="Vendor (any)")
                                                # factory=VendorAnyFilter, joiner=join_vendor_any)

        g.default_sortkey = 'upc'

        product_link = lambda p: self.get_action_url('view', p)

        g.upc.set(renderer=forms.renderers.GPCFieldRenderer)
        g.upc.attrs(link=product_link)

        g.description.set(renderer=DescriptionFieldRenderer)
        g.description.attrs(link=product_link)

        g.regular_price.set(renderer=forms.renderers.PriceFieldRenderer)
        g.current_price.set(renderer=forms.renderers.PriceFieldRenderer)
        g.configure(
            include=[
                g.upc.label("UPC"),
                g.brand,
                g.description,
                g.size,
                g.subdepartment,
                g.vendor.label("Pref. Vendor"),
                g.regular_price.label("Reg. Price"),
                g.current_price.label("Cur. Price"),
                ],
            readonly=True)

        # TODO: need to check for 'print labels' permission here also
        if self.print_labels:
            g.more_actions.append(grids.GridAction('print_label', icon='print'))

    def template_kwargs_index(self, **kwargs):
        if self.print_labels:
            kwargs['label_profiles'] = Session.query(model.LabelProfile)\
                                              .filter(model.LabelProfile.visible == True)\
                                              .order_by(model.LabelProfile.ordinal)\
                                              .all()
        return kwargs

    def row_attrs(self, row, i):

        attrs = {'uuid': row.uuid}

        classes = []
        if row.not_for_sale:
            classes.append('not-for-sale')
        if row.deleted:
            classes.append('deleted')
        if classes:
            attrs['class_'] = ' '.join(classes)

        return attrs

    def get_instance(self):
        key = self.request.matchdict['uuid']
        product = Session.query(model.Product).get(key)
        if product:
            return product
        price = Session.query(model.ProductPrice).get(key)
        if price:
            return price.product
        raise httpexceptions.HTTPNotFound()

    def configure_fieldset(self, fs):

        fs.upc.set(renderer=forms.renderers.GPCFieldRenderer)
        fs.brand.set(options=[])
        fs.unit_of_measure.set(renderer=forms.renderers.EnumFieldRenderer(enum.UNIT_OF_MEASURE))
        fs.regular_price.set(renderer=forms.renderers.PriceFieldRenderer)
        fs.current_price.set(renderer=forms.renderers.PriceFieldRenderer)

        fs.append(fa.Field('current_price_ends', type=fa.types.DateTime,
                           value=lambda p: p.current_price.ends if p.current_price else None))

        fs.configure(
            include=[
                fs.upc.label("UPC"),
                fs.brand.with_renderer(forms.renderers.BrandFieldRenderer),
                fs.description,
                fs.unit_size,
                fs.unit_of_measure.label("Unit of Measure"),
                fs.size,
                fs.weighed,
                fs.case_pack,
                fs.department.with_renderer(products_forms.DepartmentFieldRenderer),
                fs.subdepartment.with_renderer(products_forms.SubdepartmentFieldRenderer),
                fs.category.with_renderer(products_forms.CategoryFieldRenderer),
                fs.family,
                fs.report_code,
                fs.regular_price,
                fs.current_price,
                fs.current_price_ends,
                fs.deposit_link,
                fs.tax,
                fs.organic,
                fs.discountable,
                fs.special_order,
                fs.not_for_sale,
                fs.deleted,
                fs.last_sold,
                ])
        if not self.viewing:
            del fs.regular_price
            del fs.current_price
        if not self.request.has_perm('products.view_deleted'):
            del fs.deleted

    def template_kwargs_view(self, **kwargs):
        kwargs['image'] = False
        product = kwargs['instance']
        if product.upc:
            kwargs['image_url'] = pod.get_image_url(self.rattail_config, product.upc)
            kwargs['image_path'] = pod.get_image_path(self.rattail_config, product.upc)
            if os.path.exists(kwargs['image_path']):
                kwargs['image'] = True
        return kwargs

    def edit(self):
        # TODO: Should add some more/better hooks, so don't have to duplicate
        # so much code here.
        self.editing = True
        instance = self.get_instance()
        form = self.make_form(instance)
        product_deleted = instance.deleted
        if self.request.method == 'POST':
            if form.validate():
                self.save_form(form)
                self.after_edit(instance)
                self.request.session.flash("{} {} has been updated.".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect(self.get_action_url('view', instance))
        if product_deleted:
            self.request.session.flash("This product is marked as deleted.", 'error')
        return self.render_to_response('edit', {'instance': instance,
                                                'instance_title': self.get_instance_title(instance),
                                                'form': form})

    def make_batch(self):
        if self.request.method == 'POST':
            provider = self.request.POST.get('provider')
            if provider:
                provider = batches.get_provider(self.rattail_config, provider)
                if provider:

                    if self.request.POST.get('params') == 'True':
                        provider.set_params(Session(), **self.request.POST)

                    else:
                        try:
                            url = self.request.route_url('batch_params.{}'.format(provider.name))
                        except KeyError:
                            pass
                        else:
                            self.request.session['referer'] = self.request.current_route_url()
                            return httpexceptions.HTTPFound(location=url)
                    
                    progress = SessionProgress(self.request, 'products.batch')
                    thread = Thread(target=self.make_batch_thread, args=(provider, progress))
                    thread.start()
                    kwargs = {
                        'key': 'products.batch',
                        'cancel_url': self.request.route_url('products'),
                        'cancel_msg': "Batch creation was canceled.",
                        }
                    return render_to_response('/progress.mako', kwargs, request=self.request)

        enabled = self.rattail_config.get('rattail.pyramid', 'batches.providers')
        if enabled:
            enabled = enabled.split()

        providers = []
        for provider in batches.iter_providers():
            if not enabled or provider.name in enabled:
                providers.append((provider.name, provider.description))

        return {'providers': providers}

    def make_batch_thread(self, provider, progress):
        """
        Threat target for making a batch from current products query.
        """
        session = RattailSession()
        products = self.get_effective_query(session)
        batch = provider.make_batch(session, products, progress)
        if not batch:
            session.rollback()
            session.close()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        progress.session.load()
        progress.session['complete'] = True
        progress.session['success_url'] = self.request.route_url('batch.read', uuid=batch.uuid)
        progress.session['success_msg'] = 'Batch "{}" has been created.'.format(batch.description)
        progress.session.save()

    @classmethod
    def defaults(cls, config):

        # print labels
        config.add_tailbone_permission('products', 'products.print_labels',
                                       "Print labels for products")

        # view deleted products
        config.add_tailbone_permission('products', 'products.view_deleted',
                                       "View products marked as deleted")

        # make batch from product query
        config.add_route('products.create_batch', '/products/batch')
        config.add_view(cls, attr='make_batch', route_name='products.create_batch',
                        renderer='/products/batch.mako', permission='batches.create')

        cls._defaults(config)


class ProductVersionView(VersionView):
    """
    View which shows version history for a product.
    """
    parent_class = model.Product
    route_model_view = 'product.read'
    child_classes = [
        (model.ProductCode, 'product_uuid'),
        (model.ProductCost, 'product_uuid'),
        (model.ProductPrice, 'product_uuid'),
        ]

    def warn_if_deleted(self):
        """
        Maybe set flash warning if product is marked deleted.
        """
        uuid = self.request.matchdict['uuid']
        product = Session.query(model.Product).get(uuid)
        assert product, "No product found for UUID: {}".format(repr(uuid))
        if product.deleted:
            self.request.session.flash("This product is marked as deleted.", 'error')

    def list(self):
        self.warn_if_deleted()
        return super(ProductVersionView, self).list()

    def details(self):
        self.warn_if_deleted()
        return super(ProductVersionView, self).details()


class ProductsAutocomplete(AutocompleteView):
    """
    Autocomplete view for products.
    """
    mapped_class = model.Product
    fieldname = 'description'

    def query(self, term):
        q = Session.query(model.Product).outerjoin(model.Brand)
        q = q.filter(sa.or_(
                model.Brand.name.ilike('%{}%'.format(term)),
                model.Product.description.ilike('%{}%'.format(term))))
        if not self.request.has_perm('products.view_deleted'):
            q = q.filter(model.Product.deleted == False)
        q = q.order_by(model.Brand.name, model.Product.description)
        q = q.options(orm.joinedload(model.Product.brand))
        return q

    def display(self, product):
        return product.full_description


def products_search(request):
    """
    Locate a product(s) by UPC.

    Eventually this should be more generic, or at least offer more fields for
    search.  For now it operates only on the ``Product.upc`` field.
    """
    product = None
    upc = request.GET.get('upc', '').strip()
    upc = re.sub(r'\D', '', upc)
    if upc:
        product = api.get_product_by_upc(Session(), upc)
        if not product:
            # Try again, assuming caller did not include check digit.
            upc = GPC(upc, calc_check_digit='upc')
            product = api.get_product_by_upc(Session(), upc)
        if product:
            if product.deleted and not request.has_perm('products.view_deleted'):
                product = None
            else:
                product = {
                    'uuid':                     product.uuid,
                    'upc':                      unicode(product.upc or ''),
                    'full_description':         product.full_description,
                    }
    return {'product': product}


def print_labels(request):
    profile = request.params.get('profile')
    profile = Session.query(model.LabelProfile).get(profile) if profile else None
    if not profile:
        return {'error': "Label profile not found"}

    product = request.params.get('product')
    product = Session.query(model.Product).get(product) if product else None
    if not product:
        return {'error': "Product not found"}

    quantity = request.params.get('quantity')
    if not quantity.isdigit():
        return {'error': "Quantity must be numeric"}
    quantity = int(quantity)

    printer = profile.get_printer(request.rattail_config)
    if not printer:
        return {'error': "Couldn't get printer from label profile"}

    try:
        printer.print_labels([(product, quantity)])
    except Exception, error:
        return {'error': str(error)}
    return {}


def includeme(config):

    config.add_route('products.autocomplete', '/products/autocomplete')
    config.add_view(ProductsAutocomplete, route_name='products.autocomplete',
                    renderer='json', permission='products.list')

    config.add_route('products.print_labels', '/products/labels')
    config.add_view(print_labels, route_name='products.print_labels',
                    renderer='json', permission='products.print_labels')

    config.add_route('products.search', '/products/search')
    config.add_view(products_search, route_name='products.search',
                    renderer='json', permission='products.list')

    ProductsView.defaults(config)
    version_defaults(config, ProductVersionView, 'product')
