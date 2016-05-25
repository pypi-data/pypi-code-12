
from .. core import DocidoError


class IndexAPIError(DocidoError):
    @classmethod
    def build(cls, card):
        return IndexAPIErrorBuilder(card)


class IndexAPIErrorBuilder(object):
    def __init__(self, card, exception=None):
        """ Prepare an IndexAPIError

        :param: dict: card
          card concerned by the exception about to be raised
        """
        assert card is not None
        assert isinstance(card, dict)
        assert 'id' in card
        self.card = card
        self._message = ''
        self._exception = exception

    def message(self, message):
        """ Provides a message to the exception to be raised

        :param: basestring: message:
          additional message
        :return: this instance
        :rtype: IndexAPIErrorBuilder
        """
        self._message = message
        return self

    def exception(self):
        return IndexAPIError("in '{}' card {}: {}".format(
            self.card.get('kind'),
            self.card['id'],
            self._message)
        )
