

__all__ = ['transform', 'SourceFileTransformer', 'register_transformer']


from .base import (SourceFileTransformer, register_transformer,
    init_transformers, transformers)
from . import plimtemplate, coffeescript, stylus, md, rst, rapydscript



def transform(src_file):
    transformer = transformers.get(src_file.suffix)
    if transformer is not None:
        return transformer.mime_type, transformer.transform(src_file)
    else:
        return None
