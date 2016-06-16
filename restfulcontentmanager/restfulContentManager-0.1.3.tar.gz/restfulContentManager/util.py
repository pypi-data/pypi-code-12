def _guess_model_type(path):
    """
        Guess the type of a file.
        If allow_directory is False, don't consider the possibility that the
        file is a directory.
    """
    if path.endswith('.ipynb'):
        return 'notebook'
    elif '.' not in path.split('/')[-1]:
        return 'directory'
    else:
        return 'file'
