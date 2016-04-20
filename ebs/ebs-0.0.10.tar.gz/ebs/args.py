
def turn_docopt_arg_names_into_valid_var_names(args):
    """Makes docopt arg names into valid Python variable names.

    Enables locals.update(args) to load docopt arguments into the local
    namespace so they can be accessed with arg_name instead of
    args["--arg-name"]."""

    return {k.replace("--", "").replace("-", "_"): v for k, v in args.items()}
