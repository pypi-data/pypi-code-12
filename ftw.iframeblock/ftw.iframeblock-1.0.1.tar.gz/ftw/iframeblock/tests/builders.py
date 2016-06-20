from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class IFrameBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.iframeblock.IFrameBlock'

builder_registry.register('iframe block', IFrameBlockBuilder)
