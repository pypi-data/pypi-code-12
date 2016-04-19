from score.init import ConfiguredModule


defaults = {
}


def init(confdict):
    """
    Initializes this module acoording to the :ref:`SCORE module initialization
    guidelines <module_initialization>` with the following configuration keys:
    """
    conf = defaults.copy()
    conf.update(confdict)
    return Configured__PACKAGE_NAME_CAMELCASE__Module()


class Configured__PACKAGE_NAME_CAMELCASE__Module(ConfiguredModule):

    def __init__(self):
        import __PACKAGE_NAME__
        super().__init__(__PACKAGE_NAME__)
