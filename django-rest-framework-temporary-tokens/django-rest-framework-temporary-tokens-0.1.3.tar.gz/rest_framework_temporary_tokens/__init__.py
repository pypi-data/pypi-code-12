"""
Works with Django REST Framework and allows you to create authentication
tokens that expire within a given number of minutes and optionally
refresh the time to expiration on each successful authentication.
"""
__all__ = [
    'authentication',
    'models',
    'views'
]

__version__ = '0.1.3'
