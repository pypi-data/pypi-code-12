from cloudmesh_client.common.Shell import Shell
from cloudmesh_client.common.dotdict import dotdict


class image(object):
    @classmethod
    def list(cls):
        def convert(line):
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", "")
            entry = line.split(" ")
            data = dotdict()
            data.name = entry[0]
            data.provider = entry[1]
            data.date = entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        lines = []
        for line in result.split("\n"):
            lines.append(convert(line))
        return lines
