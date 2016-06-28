from time import time
from uuid import uuid4


def create_partner(service, **custom_attrs):
        # can't use a uuid because of 30 char limit:
        unique_id = str(time()).replace('.', '')

        attrs = {
            'id': 'WL_TEST_%s' % unique_id,
            'name': 'TEST',
            'parent_partner_id': service.username,
            'properties': {'website': 'example.com'},
        }
        attrs.update(custom_attrs)

        return service.create_partner(**attrs)


def create_user(service, **custom_attrs):
    """Create test user with default attributes.

    Override default attributes by passing keyword arguments.
    """
    attrs = {
        'email': 'test+%s@yola.com' % uuid4().hex,
        'name': 'John',
        'surname': 'Smith',
        'partner_id': service.username,
        'preferences': {},
    }
    attrs.update(custom_attrs)
    return service.create_user(**attrs)


def create_user_with_subscription(service, **custom_attrs):
    user = create_user(service, **custom_attrs)
    service.create_subscription('wl_basic', user['id'], {})
    return user


def create_site(service, user_id=None):
    """Create test site for given user_id.

    If no user id is provided, a test user will be created.
    """
    if not user_id:
        user_id = create_user_with_subscription(service)['id']

    serialized_site = {
        'id': uuid4().hex,
        'cryptoKey': uuid4().hex,
        'user_id': user_id,
        'owner_id': user_id,
        'name': 'My Test Site',
        'version': 62,
        'locale': 'en',
        'properties': {},
        'facebook_page_id': None,
        'site_type': '1',
        'auth_user': None,
        'auth_pass': None,
        'site_template': 'default',
        'base_template': 'SuperFlat_v2',
        'navigation': [],
    }

    return service._create_site(**serialized_site)
