from django.utils.decorators import method_decorator


def classBasedViewDecorator(decoratorFn):
    def decorator(cls):
        cls.dispatch=method_decorator(decoratorFn)(cls.dispatch)
        return cls
    return decorator
