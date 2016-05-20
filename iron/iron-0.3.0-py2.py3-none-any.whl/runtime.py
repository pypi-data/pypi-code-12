from .local import LocalStack


_env_stack = LocalStack()
_verbose_stack = LocalStack()

# local proxies
env = _env_stack()
verbose = _verbose_stack()
