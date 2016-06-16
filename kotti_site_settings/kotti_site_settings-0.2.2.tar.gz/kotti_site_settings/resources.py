# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from kotti import Base
from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from zope.interface import implements

from kotti_site_settings import _


class AppSettingsPage(Content):
    """Survey Content type."""

    tablename = 'setting_pages'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('contents.id'),
                primary_key=True, unique=True)
    editor_name = Column(
        Unicode,
        ForeignKey('principals.name', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True
    )

    @declared_attr
    def editor(cls):
        return relationship(
            "kotti.security.Principal",
            primaryjoin=("kotti.security.Principal.name=="
                         "AppSettingsPage.editor_name"))

    type_info = Content.type_info.copy(
        name=u'System Settings',
        title=_(u'System Settings'),
        add_view=u'add_settings',
        addable_to=[u'Document'],
        add_permission="admin"
    )


class AppSettings(Base):

    tablename = 'site_settings'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    id = Column(Unicode(100), primary_key=True, nullable=False)
    settings_id = Column(
        Integer,
        ForeignKey('setting_pages.id', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    option = Column(String, nullable=False)
    value = Column(String, default="")
