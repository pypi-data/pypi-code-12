from api_star.compat import copy_signature, getargspec
from api_star.exceptions import ValidationError
from functools import wraps


def validate(**validated):
    """
    1. The `validate()` function itself takes keyword arguments,
       and returns a decorator.
    """

    def decorator(func):
        """
        2. The decorator is called on the function that `@validate()` has been
           applied too, and returns the updated function.
        """
        # Ensure that the arguments to `@validate(...)` match the signature
        # of the function that it has been applied too.
        arg_names = getargspec(func).args

        for key in validated.keys():
            if key not in arg_names:
                raise RuntimeError(
                    '"%s" keyword argument to @validate() decorator does not '
                    'match any arguments in the function signature of %s' %
                    (key, func)
                )

        @wraps(func)  # `wraps` preserves the function name etc...
        def wrapper(*args, **kwargs):
            """
            3. When a function decorated by `@validate()` is called, this
               wrapper function is what actaully gets executed.
            """
            # Turn any positional arguments into keyword arguments instead.
            for idx, value in enumerate(args):
                key = arg_names[idx]
                kwargs[key] = value

            # Validate any inputs as required, collecting any errors.
            errors = {}
            for key, value in kwargs.items():
                if key in validated:
                    validator = validated[key]
                    try:
                        kwargs[key] = validator(value)
                    except ValidationError as exc:
                        errors[key] = exc.description

            # If any errors occured, then fail.
            if errors:
                raise ValidationError(errors)

            # Call the underlying function.
            return func(**kwargs)

        # Preserve the function signature.
        copy_signature(func, wrapper)
        return wrapper

    return decorator


def annotate(**kwargs):
    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func
    return decorator
