import glob
import importlib
import os

from loktar.exceptions import CITestFail
from loktar.exceptions import CITestUnknown
from loktar.exceptions import ImportPluginError
from loktar.log import Log


def run_test(package):
    """Run the packaging functions

    Args:
        package (dict): package_config

    Raises:
        CITestFail: some error occured during the test
        CITestUnknown: wrong value for config['test_type']
    """
    logger = Log()
    module = list()
    categories_test = dict()

    plugins = filter(lambda x: x not in ["__init__", "plugin", "strategy_test"],
                     map(lambda x: x.split(".")[0].split("/")[-1],
                         glob.glob("{0}/*.py".format(os.path.dirname(os.path.abspath(__file__))))
                         )
                     )
    try:
        # TODO removethis loop, it's useless only import and catch the import error if there is
        for id_plugin, plugin in enumerate(plugins):
            if plugin not in categories_test:
                module.append(importlib.import_module("loktar.testing.{0}".format(plugin)))
                print "{0}.{1}".format(module, plugin.capitalize())
                categories_test[plugin] = eval("{0}.{1}".format("module[{0}]".format(id_plugin), plugin.capitalize()))
        
    except ImportError as e:
        raise ImportPluginError(e)

    if package["test_type"] in categories_test:
        test_result = categories_test[package["test_type"]](package).run()
        if test_result is not None and not test_result:
            logger.error("{0} failed".format(package["test_type"].capitalize()))
            raise CITestFail

    else:
        logger.error("Unknown test type: {0}".format(package["test_type"]))
        raise CITestUnknown

if __name__ == "__main__":
    run_test({
        "pkg_type": "whl",
        "pkg_name": "connect",
        "test_type": "make",
        "type": "library"
    })
