from courspider.raw_html import get_html

class URL:

    def __init__(self, url):
        """
        Represents an URL with the escaped raw html data found at the given URL.

        :param url: the URL to look at
        :type url: str
        """
        self.url = url
        self.raw_html = get_html(url)

    def __str__(self):
        """
        Return a string representation of a URL

        :return: string representation of a URL
        :rtype: str
        """
        return self.url

    def __eq__(self, other):
        """
        Return True if and only if this URL is equal to other.

        They are equal if and only if other is an instance of an URL, and both
        URLs have the same url.

        :param other: The other object to compare to
        :type other: Object
        :return: whether or not these they are equal
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.url == other.url
        return False
