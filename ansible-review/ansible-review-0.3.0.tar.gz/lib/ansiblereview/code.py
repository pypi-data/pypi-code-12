from ansiblereview import Error, Result, utils


def code_passes_flake8(candidate, options):
    result = utils.execute("flake8 %s" % candidate.path)
    errors = []
    if result.rc:
        for line in result.output.split('\n'):
            lineno = line.split(':')[1]
            errors.append(Error(lineno, line))
    return Result(candidate.path, errors)
