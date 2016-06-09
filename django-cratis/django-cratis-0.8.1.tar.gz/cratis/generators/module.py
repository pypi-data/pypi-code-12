import os

from cratis.generators.codegen import package_to_path, generate_package, file_add_import, settings_add_feature


class ModuleFile(object):
    """
    Represent any python module
    """

    def __init__(self, package, path=None):
        super(ModuleFile, self).__init__()

        self.package = package
        self.path = path or package_to_path(package) + '.py'

        self.content = None

        self.reload()

    @property
    def exists(self):
        """
        Check if file exists on disk

        :return:
        """

        return os.path.exists(self.path)

    def reload(self):
        """
        Reload file source from file

        :return:
        """
        if not self.exists:
            self.content = None
            return

        with open(self.path) as f:
            self.content = f.read()

    def save(self):
        """
        Dump file contents to disk

        :return:
        """

        generate_package(self.package)

        with open(self.path, 'w+') as f:
            f.write(self.content)

    def add_import(self, package, name):
        self.content = file_add_import(self.content, package, (name,))


class SettingsModuleFile(ModuleFile):
    """
    Represents cratis settings module
    """

    def add_feature(self, package, name, default_code=None):
        self.content = settings_add_feature(self.content, package, name, default_code)
