def file_get_contents(filename):
        with file(filename) as f:
                s = f.read()

	return s
