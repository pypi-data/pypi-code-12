from loktar.exceptions import CITestFail
from loktar.exceptions import CITestUnknown
from loktar.exceptions import ImportPluginError
from loktar.log import Log
from loktar.plugin import find_plugin


def run_test(package):
    """Run the packaging functions

    Args:
        package (dict): package_config

    Raises:
        CITestFail: some error occured during the test
        CITestUnknown: wrong value for config['test_type']
    """
    logger = Log()

    try:
        test_runner = eval("{0}.{1}".format(find_plugin(package["test_type"]),
                                            package["test_type"].title().replace("_", "")))

    except ImportPluginError:
        raise

    try:
        test_runner.run()
    except Exception as e:
        logger.error(repr(e))
        raise CITestFail


if __name__ == "__main__":
    run_test({
        "pkg_type": "whl",
        "pkg_name": "connect",
        "test_type": "make",
        "type": "library"
    })
