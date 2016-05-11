# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Data Models for Products
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from rattail import enum
from .core import Base, uuid_column, GPCType, getset_factory
from .org import Department, Subdepartment, Category
from .vendors import Vendor


class Brand(Base):
    """
    Represents a brand or similar product line.
    """
    __tablename__ = 'brand'
    __versioned__ = {}

    uuid = uuid_column()
    name = sa.Column(sa.String(length=100))

    def __unicode__(self):
        return unicode(self.name or '')


class Tax(Base):
    """
    Represents a sales tax rate to be applied to products.
    """
    __tablename__ = 'tax'
    __table_args__ = (
        sa.UniqueConstraint('code', name='tax_uq_code'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    code = sa.Column(sa.Integer(), nullable=False)
    description = sa.Column(sa.String(length=255), nullable=True)
    rate = sa.Column(sa.Numeric(precision=7, scale=5), nullable=False)

    def __unicode__(self):
        return "{0} ({1:0.2f} %)".format(self.description, self.rate)


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """
    __tablename__ = 'product'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='product_fk_department'),
        sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'], name='product_fk_subdepartment'),
        sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'], name='product_fk_category'),
        sa.ForeignKeyConstraint(['family_uuid'], ['family.uuid'], name='product_fk_family'),
        sa.ForeignKeyConstraint(['brand_uuid'], ['brand.uuid'], name='product_fk_brand'),
        sa.ForeignKeyConstraint(['report_code_uuid'], ['report_code.uuid'], name='product_fk_report_code'),
        sa.ForeignKeyConstraint(['deposit_link_uuid'], ['deposit_link.uuid'], name='product_fk_deposit_link'),
        sa.ForeignKeyConstraint(['tax_uuid'], ['tax.uuid'], name='product_fk_tax'),
        sa.ForeignKeyConstraint(['regular_price_uuid'], ['product_price.uuid'], name='product_fk_regular_price', use_alter=True),
        sa.ForeignKeyConstraint(['current_price_uuid'], ['product_price.uuid'], name='product_fk_current_price', use_alter=True),
        sa.Index('product_ix_upc', 'upc'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    upc = sa.Column(GPCType())
    department_uuid = sa.Column(sa.String(length=32))
    subdepartment_uuid = sa.Column(sa.String(length=32))
    category_uuid = sa.Column(sa.String(length=32))
    family_uuid = sa.Column(sa.String(length=32))

    report_code_uuid = sa.Column(sa.String(length=32), nullable=True, doc=u"""\
UUID of the product's report code, if any.
""")

    deposit_link_uuid = sa.Column(sa.String(length=32), nullable=True, doc="""
UUID of the product's deposit link, if any.
""")

    deposit_link = orm.relationship('DepositLink', doc="""
Reference to the :class:`DepositLink` instance with which the product
associates, if any.
""")

    tax_uuid = sa.Column(sa.String(length=32), nullable=True, doc="""
UUID of the product's tax, if any.
""")

    tax = orm.relationship(Tax, doc="""
Reference to the :class:`Tax` instance with which the product associates, if
any.
""")

    brand_uuid = sa.Column(sa.String(length=32))
    description = sa.Column(sa.String(length=60))
    description2 = sa.Column(sa.String(length=60))
    size = sa.Column(sa.String(length=30))

    unit_size = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
Unit size for product, as decimal.  This refers to the numeric size of a unit
of the product, in terms of the :attr:`unit_of_measure`, and may be used for
smarter price comparisons etc.
""")

    unit_of_measure = sa.Column(sa.String(length=4), nullable=False,
                                default=enum.UNIT_OF_MEASURE_NONE, doc="""
Code indicating the unit of measure for the product.  Value should be one of
the keys of the ``rattail.enum.UNIT_OF_MEASURE`` dictionary.
""")

    weighed = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Whether or not the product must be weighed to determine its final price.
""")

    case_pack = sa.Column(sa.Integer(), nullable=True, doc="""
Pack size for the product, i.e. how many units are in a case.
""")

    organic = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Whether the item is organic.
""")

    not_for_sale = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate items which are not available for sale.
""")

    deleted = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate items which have been deleted.  Obviously this is implies
"false" deletion, where the record is actually kept on file.  Whether or not
you use this is up to you.
""")

    regular_price_uuid = sa.Column(sa.String(length=32))
    current_price_uuid = sa.Column(sa.String(length=32))

    discountable = sa.Column(sa.Boolean(), nullable=False, default=True, doc="""
Whether or not the product may be discounted in any way.
""")

    special_order = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Whether the product is available for special order.
""")

    last_sold = sa.Column(sa.DateTime(), nullable=True, doc="""
UTC timestamp of the product's last sale event.
""")

    department = orm.relationship(Department, order_by=Department.name)

    subdepartment = orm.relationship(
        Subdepartment,
        order_by=Subdepartment.name,
        backref=orm.backref('products', cascade='all'))

    category = orm.relationship(
        Category, back_populates='products')

    brand = orm.relationship(Brand)

    family = orm.relationship(
        u'Family', back_populates=u'products', doc=u"""\
Reference to the :class:`Family` instance with which the product associates, if
any.
""")

    report_code = orm.relationship(
        u'ReportCode', back_populates=u'products', doc=u"""\
Reference to the :class:`ReportCode` instance with which the product
associates, if any.
""")

    def __unicode__(self):
        return self.full_description

    @property
    def full_description(self):
        """
        Convenience attribute which returns a more complete description.

        Most notably, this includes the brand name and product size.
        """
        fields = [
            (self.brand.name or '') if self.brand else '',
            self.description or '',
            self.size or '']
        fields = [f.strip() for f in fields if f.strip()]
        return ' '.join(fields)

    @property
    def pretty_upc(self):
        """
        Product's UPC as a somewhat human-readable string.
        """
        if self.upc is None:
            return None
        return self.upc.pretty()

    def cost_for_vendor(self, vendor):
        """
        Of the product's cost records, return the first one associated with the
        given vendor.
        """
        for cost in self.costs:
            if cost.vendor is vendor:
                return cost


Category.products = orm.relationship(
    Product, back_populates='category')


class ProductCode(Base):
    """
    Represents an arbitrary "code" for a product.
    """
    __tablename__ = 'product_code'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_code_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20))

    def __unicode__(self):
        return unicode(self.code or '')


Product._codes = orm.relationship(
    ProductCode, backref='product',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=ProductCode.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Product.codes = association_proxy(
    '_codes', 'code',
    getset_factory=getset_factory,
    creator=lambda c: ProductCode(code=c))

Product._code = orm.relationship(
    ProductCode,
    primaryjoin=sa.and_(
        ProductCode.product_uuid == Product.uuid,
        ProductCode.ordinal == 1,
        ),
    uselist=False,
    viewonly=True)

Product.code = association_proxy(
    '_code', 'code',
    getset_factory=getset_factory)


class ProductCost(Base):
    """
    Represents a source from which a product may be obtained via purchase.
    """
    __tablename__ = 'product_cost'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_cost_fk_product'),
        sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='product_cost_fk_vendor'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20))

    case_size = sa.Column(sa.Integer())
    case_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    pack_size = sa.Column(sa.Integer())
    pack_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    effective = sa.Column(sa.DateTime())

    vendor = orm.relationship(
        Vendor,
        backref=orm.backref('product_costs', cascade='all'))


Product.costs = orm.relationship(
    ProductCost, backref='product',
    collection_class=ordering_list('preference', count_from=1),
    order_by=ProductCost.preference,
    cascade='save-update, merge, delete, delete-orphan')

Product.cost = orm.relationship(
    ProductCost,
    primaryjoin=sa.and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    uselist=False,
    viewonly=True)

Product.vendor = orm.relationship(
    Vendor,
    secondary=ProductCost.__table__,
    primaryjoin=sa.and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    secondaryjoin=Vendor.uuid == ProductCost.vendor_uuid,
    uselist=False,
    viewonly=True)


class ProductPrice(Base):
    """
    Represents a price for a product.
    """
    __tablename__ = 'product_price'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_price_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    type = sa.Column(sa.Integer())
    level = sa.Column(sa.Integer())
    starts = sa.Column(sa.DateTime())
    ends = sa.Column(sa.DateTime())
    price = sa.Column(sa.Numeric(precision=8, scale=3))
    multiple = sa.Column(sa.Integer())
    pack_price = sa.Column(sa.Numeric(precision=8, scale=3))
    pack_multiple = sa.Column(sa.Integer())


Product.prices = orm.relationship(
    ProductPrice, backref='product',
    primaryjoin=ProductPrice.product_uuid == Product.uuid,
    cascade='save-update, merge, delete, delete-orphan')

Product.regular_price = orm.relationship(
    ProductPrice,
    primaryjoin=Product.regular_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)

Product.current_price = orm.relationship(
    ProductPrice,
    primaryjoin=Product.current_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)
