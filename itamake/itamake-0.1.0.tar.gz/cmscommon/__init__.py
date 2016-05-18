import six

LANG_C = "c"
LANG_CPP = "cpp"
LANG_PASCAL = "pas"
LANG_PYTHON = "py"
LANG_PHP = "php"
LANG_JAVA = "java"

def get_compilation_commands(language, source_filenames, executable_filename,
                             for_evaluation=True):
    """Return the compilation commands.

    The compilation commands are for the specified language, source
    filenames and executable filename. Each command is a list of
    strings, suitable to be passed to the methods in subprocess
    package.

    language (string): one of the recognized languages.
    source_filenames ([string]): a list of the string that are the
        filenames of the source files to compile; the order is
        relevant: the first file must be the one that contains the
        program entry point (with some langages, e.g. Pascal, only the
        main file must be passed to the compiler).
    executable_filename (string): the output file.
    for_evaluation (bool): if True, define EVAL during the compilation;
        defaults to True.

    return ([[string]]): a list of commands, each a list of strings to
        be passed to subprocess.

    """
    commands = []
    if language == LANG_C:
        command = ["/usr/bin/gcc"]
        if for_evaluation:
            command += ["-DEVAL"]
        command += ["-static", "-O2", "-std=c11",
                    "-o", executable_filename]
        command += source_filenames
        command += ["-lm"]
        commands.append(command)
    elif language == LANG_CPP:
        command = ["/usr/bin/g++"]
        if for_evaluation:
            command += ["-DEVAL"]
        command += ["-static", "-O2", "-std=c++11",
                    "-o", executable_filename]
        command += source_filenames
        commands.append(command)
    elif language == LANG_PASCAL:
        command = ["/usr/bin/fpc"]
        if for_evaluation:
            command += ["-dEVAL"]
        command += ["-XS", "-O2", "-o%s" % executable_filename]
        command += [source_filenames[0]]
        commands.append(command)
    elif language == LANG_PYTHON:
        # The executable name is fixed, and there is no way to specify
        # the name of the pyc, so we need to bundle together two
        # commands (compilation and rename).
        # In order to use Python 3 change them to:
        # /usr/bin/python3 -m py_compile %s
        # mv __pycache__/%s.*.pyc %s
        py_command = ["/usr/bin/python2", "-m", "py_compile",
                      source_filenames[0]]
        mv_command = ["/bin/mv", "%s.pyc" % os.path.splitext(os.path.basename(
                      source_filenames[0]))[0], executable_filename]
        commands.append(py_command)
        commands.append(mv_command)
    elif language == LANG_PHP:
        command = ["/bin/cp", source_filenames[0], executable_filename]
        commands.append(command)
    elif language == LANG_JAVA:
        class_name = os.path.splitext(source_filenames[0])[0]
        command = ["/usr/bin/gcj", "--main=%s" % class_name, "-O3", "-o",
                   executable_filename] + source_filenames
        commands.append(command)
    else:
        raise ValueError("Unknown language %s." % language)
    return commands

def utf8_decoder(value):
    """Decode given binary to text (if it isn't already) using UTF8.

    value (string): value to decode.

    return (unicode): decoded value.

    raise (TypeError): if value isn't a string.

    """
    if isinstance(value, six.text_type):
        return value
    elif isinstance(value, six.binary_type):
        return value.decode('utf-8')
    else:
        raise TypeError("Not a string.")
