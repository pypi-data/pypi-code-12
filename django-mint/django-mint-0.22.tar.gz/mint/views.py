from django.conf import settings


def with_id(request, ctx, idx, action=None):
    coordinator = get_coordinator()
    api = coordinator(request, ctx, idx=idx, action=action)
    return api.run()


def without_id(request, ctx, action=None):
    coordinator = get_coordinator()
    api = coordinator(request, ctx, action=action)
    return api.run()


def get_coordinator():
    split = settings.REST_COORDINATOR_PATH.split(".")
    path = ".".join(split[:-1])
    mod = __import__(path, fromlist=[split[-1:][0]])
    return getattr(mod, split[-1:][0])