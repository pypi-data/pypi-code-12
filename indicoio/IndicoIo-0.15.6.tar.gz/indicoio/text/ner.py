from indicoio.utils.api import api_handler
from indicoio.utils.decorators import detect_batch_decorator

@detect_batch_decorator
def people(text, cloud=None, batch=None, api_key=None, version=2, **kwargs):
    """
    Given input text, returns references to specific persons found in the text

    Example usage:

    .. code-block:: python

       >>> text = "London Underground's boss Mike Brown warned that the strike ..."
       >>> entities = indicoio.people(text)
        [
          {
            u'text': "Mike Brown",
            u'confidence': 0.09470917284488678,
            u'position': [26, 36]
          },
          ...
        ]

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of language probability pairs
    """
    url_params = {"batch": batch, "api_key": api_key, "version": version}
    return api_handler(text, cloud=cloud, api="people", url_params=url_params, **kwargs)


@detect_batch_decorator
def places(text, cloud=None, batch=None, api_key=None, version=2, **kwargs):
    """
    Given input text, returns references to specific places found in the text

    Example usage:

    .. code-block:: python

       >>> text = "London Underground's boss Mike Brown warned that the strike ..."
       >>> entities = indicoio.places(text)
        [
          {
            u'text': "London",
            u'confidence': 0.18549786508083344,
            u'position': [0, 6]
          },
          ...
        ]

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of language probability pairs
    """
    url_params = {"batch": batch, "api_key": api_key, "version": version}
    return api_handler(text, cloud=cloud, api="places", url_params=url_params, **kwargs)



@detect_batch_decorator
def organizations(text, cloud=None, batch=None, api_key=None, version=2, **kwargs):
    """
    Given input text, returns references to specific organizations found in the text

    Example usage:

    .. code-block:: python

       >>> text = "London Underground's boss Mike Brown warned that the strike ..."
       >>> entities = indicoio.organizations(text)
        [
          {
            u'text': "London Underground",
            u'confidence': 0.8643872141838074,
            u'position': [0, 18]
          }
        ]

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of language probability pairs
    """
    url_params = {"batch": batch, "api_key": api_key, "version": version}
    return api_handler(text, cloud=cloud, api="organizations", url_params=url_params, **kwargs)
