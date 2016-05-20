from ..core import ExternalCommandTask


class external_command(ExternalCommandTask):
    def process(self, inputs):
        for t, c, m in inputs:
            yield t, [self.run_external(self.cmd, input=b''.join(c))], m
