from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders


class HtmlBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.htmlblock.HtmlBlock'

builder_registry.register('html block', HtmlBlockBuilder)
