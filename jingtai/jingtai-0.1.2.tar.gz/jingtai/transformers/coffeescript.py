import subprocess
from .base import SourceFileTransformer, register_transformer


@register_transformer
class CoffeeScriptTransformer(SourceFileTransformer):
    input_ext = '.coffee'
    output_ext = '.js'
    mime_type = 'text/javascript'

    def transform(self, src):
        cmd = ['coffee', '-c', '-p', str(src)]
        return subprocess.check_output(cmd)

    def build(self, src, dest_dir):
        cmd = ['coffee', '-c', '-o', str(dest_dir), str(src)]
        return subprocess.call(cmd)
