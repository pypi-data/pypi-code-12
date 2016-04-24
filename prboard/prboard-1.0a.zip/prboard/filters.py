class BaseFilter(object):
    """
    BaseFilter to apply filters on Repo/PullRequest objects.
    """

    def __init__(self, filter_value='', wildcard=False):
        """

        Args:
            filter_value (str or sequence or int): Filter string to
        """
        self.filter_value = isinstance(filter_value, str) and filter_value.lower() or filter_value
        self.wildcard = wildcard

    @property
    def filter_on(self):
        raise NotImplementedError

    def __call__(self, obj, *args, **kwargs):
        """

        Args:
            obj (Repo or PullRequest): Filter object either repo or PR
            wildcard(bool): Boolean representing if a wildcard match is to be done or not.
            *args:
            **kwargs:

        Returns:
            bool: True or False based on the filter

        """
        self.obj = obj

        if self.wildcard:
            return self.filter_value in self.filter_on
        else:
            return self.filter_value == self.filter_on


class PRFilter(BaseFilter):
    """
    Filter to apply filters on PR. Filters title based on filter string
    """
    @property
    def filter_on(self):
        """

        Returns:

        """

        return self.obj.pr.title.lower()


class PRNumberFilter(BaseFilter):
    """
    Filter to apply filters on PR. Filters title based on filter string
    """
    @property
    def filter_on(self):
        """

        Returns:

        """

        return self.obj.pr.number

    def __call__(self, obj, *args, **kwargs):
        """

        Args:
            obj (Repo or PullRequest): Filter object either repo or PR
            wildcard(bool): Boolean representing if a wildcard match is to be done or not.
            *args:
            **kwargs:

        Returns:
            bool: True or False based on the filter

        """
        self.obj = obj

        return int(self.filter_value) == int(self.filter_on)


class LabelFilter(PRFilter):

    @property
    def filter_on(self):
        """

        Returns:

        """

        return self.obj.labels

    def __call__(self, obj, *args, **kwargs):
        """

        Args:
            *args:
            **kwargs:

        Returns:

        """
        self.obj = obj
        filter_on = self.filter_on
        if isinstance(self.filter_value, (list, tuple)):
            return all([label in filter_on for label in self.filter_value])
        else:
            return self.filter_value in filter_on


class MileStoneFilter(PRFilter):
    @property
    def filter_on(self):
        """

        Returns:

        """
        return self.obj.pr.milestone.lower()


class RepoFilter(BaseFilter):
    @property
    def filter_on(self):
        """

        Returns:

        """
        return self.obj.name.lower()
