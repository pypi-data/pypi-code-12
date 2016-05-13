"""
nose-long-descriptions - Improves nose test description output

By default, a nose test description is either the first line of its docstring,
or its id.  Enabling this plugin means that it uses both, both are present.
"""
# pylint: disable=invalid-name,no-self-use
from nose.plugins import Plugin


class EnhancedDescriptions(Plugin):
    """
    Nose Plugin to improve the descriptive output of verbose test runs.
    """

    name = 'enhanced-descriptions'

    def describeTest(self, test):
        """
        The description of a test consists of its id
         and optionally the first line of its shortDescription.
        """

        test_id = get_id(test)
        doc = get_docstring(test)

        return "%s\n\t(%s)" % (
            test_id,
            doc.partition("\n")[0]or ""
        ) if doc else test_id


def get_id(test):
    """
    Return the id of the given test, formatted as   The id is
    :param test:
    :return:
    """
    test_id = test.id()
    module_length = len(test.test.__module__)
    return test_id[:module_length] + ":" + test_id[module_length + 1:]


def get_docstring(test):
    """
    Return the docstring from a nose test

    :param test: a nose.case.Test instance
    :return: The docstring of the given test,
        with trailing and leading whitespace removed.
    """

    # Sadly, a protected member seems to be the only way to get to the docstring.
    doc = test.test._testMethodDoc
    if doc:
        return doc.strip()
