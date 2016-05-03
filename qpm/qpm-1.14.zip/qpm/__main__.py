from qpm.packaging.auto_argument_parser import AutoArgumentParser
from qpm.packaging.package_manager import PackageManager
import pkg_resources


def main():
    print 'QPM - QualiSystems Package Manager, Version: ' + pkg_resources.get_distribution("qpm").version
    auto_argument_parser = AutoArgumentParser(PackageManager)
    auto_argument_parser.parse_args()


if __name__ == "__main__":
    main()
