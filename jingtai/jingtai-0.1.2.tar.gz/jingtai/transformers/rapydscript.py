import subprocess
from .base import SourceFileTransformer, register_transformer


@register_transformer
class RapydScriptTransformer(SourceFileTransformer):
    input_ext = '.pyj'
    output_ext = '.js'
    mime_type = 'text/javascript'

    def transform(self, src):
        cmd = ['rapydscript', str(src)]
        return subprocess.check_output(cmd)

    def build(self, src, dest_dir):
        cmd = ['rapydscript', '-o', str(self.get_dest_file(src, dest_dir)), str(src)]
        return subprocess.call(cmd)
