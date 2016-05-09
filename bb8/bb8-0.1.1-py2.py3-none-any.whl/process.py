import subprocess


class CommandError(Exception):
    def __init__(self, cmd, output, returncode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd = cmd
        self.output = output
        self.returncode = returncode

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def __repr__(self, *args, **kwargs):
        return 'Command Error: {0}\nCommand: {1}\nDetail: {2}' \
            .format(self.returncode, self.cmd, self.output)


def run_cmd(cmd, **kwargs):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, **kwargs)

    out, tmp = p.communicate()
    # print(out)
    # print(p.returncode)
    # print(p.stdout)

    if p.returncode:
        raise CommandError(cmd, out, p.returncode)

    return out.decode("utf-8")
