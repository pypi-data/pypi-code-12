
transformer_classes = []
transformers = {}


def register_transformer(transformer_cls):
    transformer_classes.append(transformer_cls)
    return transformer_cls


def init_transformers(site):
    for cls in transformer_classes:
        transformers[cls.input_ext] = cls(site)


class SourceFileTransformer(object):
    # Must set this variables in subclasses:
    input_ext = None
    mime_type = None
    output_ext = None

    def __init__(self, site):
        self.site = site

    def transform(self, src):
        return NotImplementedError()

    def get_dest_file(self, src, dest_dir):
        return dest_dir / (src.stem + self.output_ext)

    def build(self, src, dest_dir):
        with self.get_dest_file(src, dest_dir).open('w') as fp:
            fp.write(self.transform(src))
